import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="games.audit_roulette_play")
def audit_roulette_play(self, payload):
    logger.info("Audit roulette play processed asynchronously: %s", payload)
    return {"status": "audited", "task_id": self.request.id}
