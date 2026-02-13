# infrastructure/services/basic_prize_calculator.py

from domain.services.prize_calculator import PrizeCalculator


class BasicPrizeCalculator(PrizeCalculator):

    def calculate(self, bet):
        # regla simple de ejemplo
        return bet.amount * 2