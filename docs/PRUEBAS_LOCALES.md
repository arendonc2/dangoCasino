# Pruebas locales del proyecto

## Objetivo

Este documento explica cómo levantar `dangoCasino` en tu máquina local y cómo validar que la arquitectura híbrida funcione sin depender de AWS.

## Requisitos previos

- Python y Docker instalados.
- Docker Compose disponible.
- Puerto `80` libre si vas a usar Nginx localmente.
- La carpeta del proyecto abierta en una terminal.

## Servicios que debes ver

- `nginx`
- `django_web`
- `flask_roulette`
- `redis`
- `celery_worker`

## Levantar el proyecto

```bash
docker compose up --build -d
docker compose ps
```

## Validación básica de infraestructura

```bash
docker compose config
docker compose ps
docker compose exec redis redis-cli ping
```

Esperado:
- `docker compose config` no debe mostrar errores.
- `redis-cli ping` debe responder `PONG`.

## Probar health checks

```bash
curl http://localhost/health/django/
curl http://localhost/health/flask/
```

Esperado:
- Django responde con estado `ok`.
- Flask responde con estado `ok`.

## Probar endpoints JSON

```bash
curl http://localhost/api/v1/player-summary/1/
curl http://localhost/api/v1/ally-status/
curl http://localhost/api/v1/currency-rate/
```

Esperado:
- `player-summary` devuelve JSON del jugador.
- `ally-status` responde con estado del servicio aliado o su fallback.
- `currency-rate` responde con la tasa COP/USD usando adapter o fallback.

## Probar ruleta y Strangler Pattern

```bash
curl -X POST http://localhost/api/v2/roulette/play \
  -H "Content-Type: application/json" \
  -d '{"player_id":1,"bet_type":"number","bet_value":"17","amount":100}'
```

Esperado:
- Si Flask está arriba, la respuesta debe venir con `source=flask-roulette`.
- Si Flask falla o se detiene, Django debe responder con `source=django-fallback`.

## Probar fallback de ruleta

1. Detén Flask:

```bash
docker compose stop flask_roulette
```

2. Repite la jugada:

```bash
curl -X POST http://localhost/api/v2/roulette/play \
  -H "Content-Type: application/json" \
  -d '{"player_id":1,"bet_type":"number","bet_value":"17","amount":100}'
```

3. Levanta Flask otra vez:

```bash
docker compose start flask_roulette
```

## Probar Celery

```bash
docker compose logs celery_worker
```

Esperado:
- Debes ver el worker arrancado.
- Al jugar ruleta, debe aparecer la tarea `audit_roulette_play` o su registro equivalente.
- Si Celery falla, la jugada no debe fallar.

## Probar i18n

Abre en el navegador:

- `http://localhost/`
- `http://localhost/games/register/`
- `http://localhost/games/play-roulette/`
- `http://localhost/games/games/`
- `http://localhost/games/system-status/`

Verifica:
- Selector de idioma.
- Cambio entre español e inglés.
- Textos traducibles en pantalla.

## Probar la UI

Revisa manualmente:

- Navegación clara desde Home.
- Botones visibles para Registro, Ruleta, Juegos y System Status.
- Mensajes de fallback legibles.
- Sin errores técnicos crudos en pantalla.

## Persistencia de saldos y apuestas

El saldo de los usuarios **no** se guarda en `auth_user`. Se guarda en la tabla `games_player`, columna `balance`.

Validar en local:

```bash
sqlite3 db.sqlite3 "SELECT id, username, balance FROM games_player ORDER BY id;"
sqlite3 db.sqlite3 "SELECT id, player_id, amount, result, payout, created_at FROM games_roulettebet ORDER BY id DESC LIMIT 10;"
```

En este proyecto, Docker Compose monta `./db.sqlite3` en `/app/db.sqlite3` para `django_web` y `celery_worker`, así que los saldos/apuestas persisten al reiniciar servicios.

## Ver tablas en UI y recuperar acceso Admin

1. Abre `http://localhost/admin/`.
2. Inicia sesión con un usuario de `auth_user` que tenga `is_superuser=1`.
3. En el panel debes ver: `Players`, `Games`, `Bets`, `Roulette bets`.

Si no puedes entrar por contraseña:

```bash
docker compose exec django_web python manage.py changepassword alejo
```

Si prefieres crear otro superusuario:

```bash
docker compose exec django_web python manage.py createsuperuser
```

Para verificar desde SQL qué cuentas admin existen:

```bash
sqlite3 db.sqlite3 "SELECT id, username, is_superuser, is_active FROM auth_user ORDER BY id;"
```

Nota de persistencia:
- `docker compose down` solo baja y elimina contenedores/red; con el montaje de `db.sqlite3` los datos quedan en disco.
- Puedes perder datos si borras manualmente `db.sqlite3` o si ejecutas limpieza agresiva de Docker y además no existe respaldo.

Si en Admin solo ves `Games` y no aparecen `Players`, `Bets` o `Roulette bets`, normalmente el contenedor `django_web` está corriendo una imagen vieja. Recompila y recrea Django:

```bash
docker compose up -d --build django_web
docker compose restart nginx
```

## Comandos útiles

```bash
docker compose logs nginx
docker compose logs django_web
docker compose logs flask_roulette
docker compose logs celery_worker
docker compose restart django_web
docker compose restart flask_roulette
```

## Criterio de aceptación local

El proyecto queda validado localmente si:

- Los servicios levantan sin errores.
- Nginx enruta hacia Django y Flask.
- Los endpoints responden.
- La ruleta funciona con Flask y con fallback.
- Celery está activo.
- El idioma cambia correctamente.
- La página de System Status abre sin problemas.
