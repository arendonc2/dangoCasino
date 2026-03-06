from ..domain.builders.bet_builder import BetBuilder
from ..infrastructure.factories.prize_calculator_factory import PrizeCalculatorFactory
from ..infrastructure.repositories import BetRepository

from ..domain.services.roulette_rules import RouletteRules
from ..infrastructure.repositories import RouletteRepository, PlayerRepository

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
    

class RouletteService:
    def __init__(self, repo: RouletteRepository):
        self.repo = repo

    def play_roulette(self, user_id, bet_type, bet_value, amount):
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0.")

        current_balance = self.repo.get_player_balance(user_id)
        if amount > current_balance:
            raise ValueError("Saldo insuficiente para realizar la apuesta.")

        spun_number = RouletteRules.spin_wheel()
        win = RouletteRules.check_win(bet_type, bet_value, spun_number)
        payout = RouletteRules.calculate_payout(bet_type, amount) if win else 0

        new_balance = current_balance - amount + payout
        self.repo.update_player_balance(user_id, new_balance)

        bet_data = {
            'player_id': user_id,
            'bet_type': bet_type,
            'bet_value': bet_value,
            'amount': amount,
            'result': 'win' if win else 'lose',
            'spun_number': spun_number,
            'payout': payout
        }
        self.repo.save_roulette_bet(bet_data)

        return {
            'spun_number': spun_number,
            'win': win,
            'payout': payout,
            'new_balance': new_balance
        }
    
class AuthService:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    def register(self, username: str, balance: float):
        username = (username or "").strip()
        if not username:
            raise ValueError("Username requerido.")
        if self.player_repo.exists_username(username):
            raise ValueError("Username already exists.")
        return self.player_repo.create(username=username, balance=float(balance))

    def login(self, username: str):
        username = (username or "").strip()
        if not username:
            raise ValueError("Username requerido.")
        player = self.player_repo.get_by_username(username)
        if not player:
            raise ValueError("Username not found. Please register first.")
        return player

    def get_player(self, player_id: int):
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise ValueError("Sesión inválida.")
        return player