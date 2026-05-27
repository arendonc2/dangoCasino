try:
	from .celery import app as celery_app
except ImportError:  # pragma: no cover - keeps local management commands usable without Celery installed
	celery_app = None

__all__ = ("celery_app",)
