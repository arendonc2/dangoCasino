from ..domain.builders.bet_builder import BetBuilder
from ..infrastructure.factories.prize_calculator_factory import PrizeCalculatorFactory
from ..infrastructure.repositories import BetRepository

class BetService:
    def __init__(self, bet_repo: BetRepository):
        self.bet_repo = bet_repo

    def place_bet_and_calculate_prize(self, user_id: int, amount: float, game_type: str, user_type: str):
        balance = self.bet_repo.get_user_balance(user_id)
        
        builder = BetBuilder()
        bet = (builder.set_user_id(user_id)
                     .set_amount(amount)
                     .set_game_type(game_type)
                     .validate_balance(balance)
                     .build())
        
        calculator = PrizeCalculatorFactory.create_calculator(user_type)
        prize = calculator.calculate(bet)
        
        self.bet_repo.save_bet(bet)
        new_balance = balance - amount + prize
        self.bet_repo.update_balance(user_id, new_balance)
        
        return {"prize": prize, "new_balance": new_balance}