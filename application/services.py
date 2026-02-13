# application/services.py

from domain.builders.bet_builder import BetBuilder
from domain.factories.prize_calculator_factory import PrizeCalculatorFactory
from games.models import Player, Game


def create_bet(player_id, game_id, amount):
    player = Player.objects.get(id=player_id)
    game = Game.objects.get(id=game_id)

    # Builder
    bet = (
        BetBuilder()
        .with_player(player)
        .with_game(game)
        .with_amount(amount)
        .build()
    )

    # Factory
    calculator = PrizeCalculatorFactory.create(player)
    prize = calculator.calculate(bet)

    bet.potential_prize = prize
    bet.save()

    return bet