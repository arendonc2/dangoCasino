# infrastructure/services/mock_prize_calculator.py

from domain.services.prize_calculator import PrizeCalculator


class MockPrizeCalculator(PrizeCalculator):

    def calculate(self, bet):
        # resultado fijo para pruebas
        return 9999