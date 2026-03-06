from abc import ABC, abstractmethod
from ..domain.entities import Bet

class BetRepository(ABC):
    @abstractmethod
    def save_bet(self, bet: Bet):
        pass

    @abstractmethod
    def get_user_balance(self, user_id: int) -> float:
        pass

    @abstractmethod
    def update_balance(self, user_id: int, new_balance: float):
        pass

class DjangoBetRepository(BetRepository):
    def save_bet(self, bet: Bet):
        from ..models import BetModel  # Assume BetModel exists in games/models.py
        BetModel.objects.create(user_id=bet.user_id, amount=bet.amount, game_type=bet.game_type)

    def get_user_balance(self, user_id: int) -> float:
        from ..models import Player  # Assume Player model
        return Player.objects.get(id=user_id).balance

    def update_balance(self, user_id: int, new_balance: float):
        from ..models import Player
        player = Player.objects.get(id=user_id)
        player.balance = new_balance
        player.save()