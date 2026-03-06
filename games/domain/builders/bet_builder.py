from ..entities import Bet

class BetBuilder:
    def __init__(self):
        self._bet = Bet()

    def set_user_id(self, user_id: int):
        self._bet.user_id = user_id
        return self

    def set_amount(self, amount: float):
        if amount <= 0:
            raise ValueError("Bet amount must be positive")
        self._bet.amount = amount
        return self

    def set_game_type(self, game_type: str):
        self._bet.game_type = game_type
        return self

    def validate_balance(self, current_balance: float):
        if self._bet.amount > current_balance:
            raise ValueError("Insufficient balance")
        return self

    def build(self):
        return self._bet