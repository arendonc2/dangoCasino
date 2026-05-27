# Despliegue y pruebas en la nube

## Objetivo

Este documento explica cómo desplegar `dangoCasino` en AWS Academy EC2 y cómo validar que todo funcione en la nube antes de la sustentación.

## Requisitos previos

- Instancia EC2 disponible.
- Security Group permitiendo tráfico HTTP en el puerto `80`.
- Acceso SSH a la instancia.
- Docker y Docker Compose instalados en la VM.
- Repositorio clonado en la instancia.

## Preparación de la instancia

Ejemplo en Amazon Linux:

```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user
newgrp docker

docker --version
docker compose version
```

Si el sistema usa otro flavor de Linux, instala Docker con el gestor de paquetes correspondiente y confirma que `docker compose` esté disponible.

## Despliegue

```bash
git clone <REPO_URL>
cd <PROJECT_FOLDER>
docker compose up --build -d
docker compose ps
```

## Validación de servicios

```bash
docker compose ps
docker compose logs nginx
docker compose logs django_web
docker compose logs flask_roulette
docker compose logs celery_worker
docker compose exec redis redis-cli ping
```

Esperado:
- `nginx` debe ser el único servicio con puerto público publicado.
- `django_web`, `flask_roulette`, `redis` y `celery_worker` deben quedar internos.
- Redis debe responder `PONG`.

## Validación de endpoints en la instancia

```bash
curl http://localhost/health/django/
curl http://localhost/health/flask/
curl http://localhost/api/v1/player-summary/1/
curl http://localhost/api/v1/ally-status/
curl http://localhost/api/v1/currency-rate/
```

## Validación de ruleta en la nube

```bash
curl -X POST http://localhost/api/v2/roulette/play \
  -H "Content-Type: application/json" \
  -d '{"player_id":1,"bet_type":"number","bet_value":"17","amount":100}'
```

Verifica que la respuesta muestre una de estas fuentes:

- `flask-roulette`
- `django-fallback`

## Validación de fallback

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

3. Reinicia Flask:

```bash
docker compose start flask_roulette
```

## Validación de Celery

```bash
docker compose logs celery_worker
```

Comprueba que el worker esté levantado y que la tarea de auditoría de ruleta se dispare después de una jugada.

## Validación de i18n

Abre desde el navegador público:

- `http://<IP_PUBLICA_EC2>/`
- `http://<IP_PUBLICA_EC2>/games/register/`
- `http://<IP_PUBLICA_EC2>/games/play-roulette/`
- `http://<IP_PUBLICA_EC2>/games/games/`
- `http://<IP_PUBLICA_EC2>/games/system-status/`

Verifica:
- Selector de idioma.
- Cambio entre español e inglés.
- Mensajes claros y sin errores crudos.

## Evidencia recomendada para sustentación

- Captura de `docker compose ps`.
- Captura de `docker compose logs nginx`.
- Captura de `docker compose logs celery_worker`.
- Respuesta de `/health/django/` y `/health/flask/`.
- Jugada de ruleta con Flask y luego con fallback.
- Pantalla de `system-status`.
- Cambio de idioma en vivo.

## Comandos rápidos

```bash
docker compose ps
docker compose logs nginx
docker compose logs flask_roulette
docker compose logs celery_worker
docker compose exec redis redis-cli ping
docker compose stop flask_roulette
docker compose start flask_roulette
```

## Criterio de aceptación en nube

El despliegue queda listo si:

- La URL pública de Nginx responde.
- Los endpoints de health responden.
- La ruleta funciona con Flask y con fallback.
- Redis y Celery están activos.
- La página de System Status abre correctamente.
- El cambio de idioma funciona.
- No hay errores críticos en logs al ejecutar la demo.
