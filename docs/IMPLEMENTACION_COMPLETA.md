# Implementación completa realizada en Dango Casino

## 1) Objetivo de esta entrega

Este documento resume **todo lo implementado** durante la sesión de trabajo: arquitectura, backend, frontend, persistencia de datos, operación local con Docker, panel administrativo y correcciones visuales/funcionales.

## 2) Arquitectura final implementada

Se consolidó una arquitectura híbrida con patrón Strangler:

- **Nginx** como punto de entrada único (puerto 80).
- **Django** como aplicación principal (UI, sesiones, persistencia, fallback).
- **Flask** como microservicio de ruleta (`/api/v2/roulette/play`).
- **Redis + Celery** para tareas asíncronas (auditoría de jugadas).
- **SQLite** como base de datos activa (`db.sqlite3`).

### Flujo principal de ruleta

1. Usuario inicia sesión o se registra en Django.
2. Usuario selecciona apuesta y monto desde la UI de ruleta.
3. Django valida sesión, apuesta y saldo.
4. Django intenta procesar con Flask (`RouletteServiceClient`).
5. Si Flask falla, Django usa fallback local (`RouletteService`).
6. Django persiste jugada y actualiza saldo en transacción.
7. Django lanza auditoría asíncrona por Celery.
8. UI muestra resultado final y saldo actualizado desde DB.

## 3) Backend implementado

### 3.1 Autenticación por sesión para jugador

Se implementaron/ajustaron los flujos:

- `LoginView`: inicio de sesión por `username`.
- `RegisterView`: creación de jugador con saldo inicial y auto-login.
- `LogoutView`: cierre de sesión.
- `get_current_player(request, for_update=False)` para resolver sesión -> jugador DB.

Beneficio:
- La UI y las jugadas trabajan con jugador real en DB, no con datos efímeros.

### 3.2 Ruleta robusta con validaciones de negocio

En `RouletteView` se implementó:

- Validación estricta de `bet_type`, `bet_value`, rango de número (0-36), y monto > 0.
- Bloqueo por saldo insuficiente antes de procesar.
- Manejo consistente para peticiones HTML/JSON.

### 3.3 Consistencia financiera transaccional

Se reforzó el flujo financiero con:

- `transaction.atomic()` para la operación completa.
- Lectura del jugador con lock (`select_for_update`) vía `get_current_player(..., for_update=True)`.
- Cálculo y guardado de `balance_before` y `balance_after`.
- Persistencia explícita del saldo actualizado en `Player.balance`.

Resultado:
- Se evita incoherencia de saldo ante concurrencia o fallos intermedios.

### 3.4 Integración Flask-first con fallback Django

Se dejó un flujo resiliente:

- Primario: Flask (`/api/v2/roulette/play`).
- Fallback: lógica de dominio en Django si Flask no responde correctamente.
- Campo `source` en resultado para trazabilidad (`flask-roulette` o `django-fallback`).

### 3.5 Reglas de ruleta corregidas

Ajustes aplicados en dominio Django y Flask:

- Giro incluye `0` (0-36).
- Apuesta `odd/even` excluye `0`.
- Validaciones más estrictas para tipos/valores de apuesta.

### 3.6 Auditoría asíncrona

Se agregó tarea Celery:

- `games.audit_roulette_play`
- Registra payload de jugada para auditoría asíncrona.
- Si falla la cola, la jugada principal **no falla**.

### 3.7 Endpoints de soporte

Se consolidaron endpoints para observabilidad funcional:

- `health/django/`
- `health/flask/`
- `api/v1/player-summary/<id>/`
- `api/v1/ally-status/`
- `api/v1/currency-rate/`
- `games/system-status/`

### 3.8 Adapter + DIP para tasa de cambio

Se implementó integración desacoplada de tasa COP->USD:

- Puerto en capa de aplicación.
- Adapter en infraestructura.
- Soporte de mock/fallback cuando API externa no está disponible.

## 4) Frontend implementado

### 4.1 Flujo UX simplificado

Se alineó el flujo de usuario a:

1. Crear cuenta.
2. Iniciar sesión.
3. Jugar ruleta.

Cambios clave:

- Navegación más clara y menos técnica.
- Balance visible en navbar para usuario autenticado.
- Mensajes de error/éxito entendibles para usuario final.

### 4.2 Tablero de apuestas visual

Se reemplazó entrada manual por UI visual:

- Selección por casillas numéricas (0-36).
- Apuestas externas (rojo/negro/par/impar).
- Inputs ocultos (`bet_type`, `bet_value`) controlados por selección UI.
- Resumen de apuesta seleccionada.

### 4.3 Animación de ruleta y tensión

Se implementó experiencia de giro con etapas:

- Estado de giro.
- Mensajes de tensión ("está girando", "por caer", "casi resultado").
- Revelado de resultado al finalizar animación.
- Botón de giro deshabilitado para evitar doble envío.

### 4.4 Corrección visual de números en rueda

Se corrigió la distribución y legibilidad de etiquetas en la rueda:

- Centrado por sector.
- Orientación legible de texto en todo el perímetro.
- Ajuste de transformaciones CSS/JS para evitar números invertidos.

## 5) Datos y persistencia

### 5.1 Dónde se guarda cada cosa

- Usuarios admin/login Django: `auth_user`.
- Jugadores del casino y saldo: `games_player.balance`.
- Historial de apuestas ruleta: `games_roulettebet`.

### 5.2 Persistencia al bajar contenedores

Se ajustó `docker-compose.yml` para montar SQLite en host:

- `./db.sqlite3:/app/db.sqlite3` en `django_web`.
- `./db.sqlite3:/app/db.sqlite3` en `celery_worker`.

Impacto:
- `docker compose down` no elimina saldos/apuestas mientras el archivo `db.sqlite3` exista en el proyecto.

## 6) Panel administrativo (Django Admin)

Se habilitó visibilidad real de datos de negocio:

- Registro de modelos: `Player`, `Game`, `Bet`, `RouletteBet`.
- Configuración útil en admin (`list_display`, filtros, búsqueda).

Además se diagnosticó y documentó el caso donde solo aparecía `Game`:

- Causa: contenedor con imagen vieja.
- Solución: rebuild de `django_web` + restart de `nginx`.

## 7) Operación, compatibilidad y despliegue local

### 7.1 Compatibilidad de dependencias

Se corrigió incompatibilidad Python/Django:

- Fijado `Django==5.2.14` para entorno Python 3.10.

### 7.2 Contenedores operativos

Servicios activos en compose:

- `nginx`
- `django_web`
- `flask_roulette`
- `redis`
- `celery_worker`

### 7.3 Documentación operativa entregada

Se generó/ajustó documentación para ejecución y verificación:

- `docs/PRUEBAS_LOCALES.md`
- `docs/DESPLIEGUE_Y_PRUEBAS_NUBE.md`
- `docs/AWS_EC2_RUNBOOK.md`
- `docs/SUSTENTACION_CHECKLIST.md`

## 8) Evidencias funcionales validadas

Durante las pruebas se validó:

- Servicios arriba por `docker compose ps`.
- Respuesta de health checks Django/Flask.
- Respuesta de admin por HTTP.
- Persistencia real en SQLite consultando tablas.
- Existencia de superusuarios en `auth_user`.
- Registro y visualización de apuestas con payout/result.

## 9) Troubleshooting incorporado

Se dejó guía para incidentes comunes:

- No aparecen tablas en Admin -> rebuild de `django_web`.
- No acceso por contraseña de admin -> `changepassword` o `createsuperuser`.
- Duda sobre pérdida de datos -> ver montajes de `db.sqlite3`.

## 10) Estado final

El sistema quedó con:

- Arquitectura híbrida operativa (Django + Flask + Nginx + Redis + Celery).
- Flujo de usuario completo y entendible.
- Ruleta visual mejorada con animación y correcciones de legibilidad.
- Consistencia financiera con persistencia transaccional.
- Panel admin útil para inspección de datos.
- Documentación de operación local y troubleshooting.
