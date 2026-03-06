from abc import ABC, abstractmethod
from ..domain.entities import Bet
from django.db.models import F

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
        from ..models import Bet  # Changed from BetModel to Bet
        Bet.objects.create(player_id=bet.user_id, game_id=1, amount=bet.amount)  # Adjust game_id if needed

    def get_user_balance(self, user_id: int) -> float:
        from ..models import Player  # Assume Player model
        return Player.objects.get(id=user_id).balance

    def update_balance(self, user_id: int, new_balance: float):
        from ..models import Player
        Player.objects.filter(id=user_id).update(balance=new_balance)

class RouletteRepository(ABC):
    @abstractmethod
    def save_roulette_bet(self, bet_data):
        pass

    @abstractmethod
    def get_player_balance(self, user_id: int) -> float:
        pass

    @abstractmethod
    def update_player_balance(self, user_id: int, new_balance: float):
        pass


class DjangoRouletteRepository(RouletteRepository):
    def save_roulette_bet(self, bet_data):
        from ..models import RouletteBet
        RouletteBet.objects.create(**bet_data)

    def get_player_balance(self, user_id: int) -> float:
        from ..models import Player
        return float(Player.objects.get(id=user_id).balance)

    def update_player_balance(self, user_id: int, new_balance: float):
        from ..models import Player
        Player.objects.filter(id=user_id).update(balance=new_balance)