# Guía de implementación — Carrito de Recarga Dango Casino

## Archivos entregados y dónde ubicarlos

| Archivo entregado        | Destino en tu proyecto                        |
|--------------------------|-----------------------------------------------|
| `deposit_model.py`       | Pegar al final de `games/models.py`           |
| `deposit_view.py`        | Pegar al final de `games/views.py`            |
| `deposit_urls_tasks.py`  | Ver instrucciones de URLs y tasks abajo       |
| `deposit_admin.py`       | Pegar al final de `games/admin.py`            |
| `deposit.html`           | Crear como `templates/games/deposit.html`     |
| `navbar_snippet.html`    | Editar `templates/base.html` (ver instrucciones) |

---

## Paso 1 — Agregar el modelo

En `games/models.py`, pega al final el contenido de `deposit_model.py`.

---

## Paso 2 — Crear y aplicar la migración

```bash
# Dentro del contenedor django_web:
docker compose exec django_web python manage.py makemigrations games
docker compose exec django_web python manage.py migrate
```

Esto crea la tabla `games_deposit` en SQLite.

---

## Paso 3 — Agregar la vista

En `games/views.py`, pega al final el contenido de `deposit_view.py`.

Ajusta los dos helpers según tu proyecto:
- Si ya tienes `get_current_player(request)`, úsalo en `_get_player()`.
- Ajusta el nombre de tu URL de login (`redirect("login")`) y de ruleta (`redirect("roulette")`).

---

## Paso 4 — Registrar la URL

En `games/urls.py`, agrega dentro de `urlpatterns`:

```python
from .views import DepositView   # agrega al bloque de imports

path("deposit/", DepositView.as_view(), name="deposit"),
```

---

## Paso 5 — Agregar la tarea Celery (opcional pero recomendado)

En `games/tasks.py`, agrega al final:

```python
@shared_task(name="games.audit_deposit")
def audit_deposit(deposit_id: int):
    from .models import Deposit
    try:
        deposit = Deposit.objects.get(id=deposit_id)
        logger.info(
            f"[AUDIT DEPOSIT] id={deposit.id} | player={deposit.player_id} | "
            f"amount={deposit.amount} | balance_after={deposit.balance_after}"
        )
    except Deposit.DoesNotExist:
        logger.warning(f"[AUDIT DEPOSIT] Depósito {deposit_id} no encontrado.")
```

---

## Paso 6 — Registrar en Admin

En `games/admin.py`, agrega al bloque de imports:

```python
from .models import Deposit   # agregar al import existente
```

Luego pega el contenido de `deposit_admin.py`.

---

## Paso 7 — Template del carrito

Crea el archivo `templates/games/deposit.html` con el contenido de `deposit.html`.

> **Nota:** Verifica que `{% load humanize %}` esté disponible.
> Si no, agrega `'django.contrib.humanize'` a `INSTALLED_APPS` en `settings.py`.

---

## Paso 8 — Navbar

En `templates/base.html`, dentro del bloque del navbar donde ya muestras el saldo,
agrega el link del carrito siguiendo el snippet de `navbar_snippet.html`.

---

## Paso 9 — Reiniciar contenedores

```bash
docker compose restart django_web celery_worker
```

O si cambiaste `settings.py`:

```bash
docker compose up --build django_web celery_worker
```

---

## Verificación rápida

```bash
# 1. Revisar que la URL existe
docker compose exec django_web python manage.py show_urls | grep deposit

# 2. Revisar que la tabla existe
docker compose exec django_web python manage.py dbshell
sqlite> .tables         -- debe listar games_deposit
sqlite> .quit

# 3. Probar desde el browser
# http://localhost/games/deposit/
```

---

## Flujo completo del usuario

```
Navbar → "+ Recargar"
  └─ GET /games/deposit/     → formulario con fichas y resumen proyectado
       └─ POST /games/deposit/
            ├─ atomic() + select_for_update()
            ├─ Player.balance += monto
            ├─ Deposit.save()
            ├─ audit_deposit.delay()   ← Celery (best-effort)
            └─ redirect → /games/roulette/  con mensaje de éxito
```
