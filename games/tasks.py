import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="games.audit_roulette_play")
def audit_roulette_play(self, payload):
    logger.info("Audit roulette play processed asynchronously: %s", payload)
    return {"status": "audited", "task_id": self.request.id}

@shared_task(name="games.audit_deposit")
def audit_deposit(deposit_id: int):
    """
    Auditoría asíncrona de depósitos.
    Igual que audit_roulette_play pero para recargas.
    """
    from .models import Deposit
    try:
        deposit = Deposit.objects.get(id=deposit_id)
        logger.info(
            f"[AUDIT DEPOSIT] id={deposit.id} | "
            f"player={deposit.player_id} | "
            f"amount={deposit.amount} | "
            f"balance_before={deposit.balance_before} | "
            f"balance_after={deposit.balance_after} | "
            f"status={deposit.status}"
        )
    except Deposit.DoesNotExist:
        logger.warning(f"[AUDIT DEPOSIT] Depósito {deposit_id} no encontrado.")
 