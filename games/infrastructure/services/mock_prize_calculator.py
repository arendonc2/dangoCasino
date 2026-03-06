# infrastructure/services/mock_prize_calculator.py

from games.domain.services.prize_calculator import PrizeCalculator


class MockPrizeCalculator(PrizeCalculator):

    def calculate(self, bet):
        # resultado fijo para pruebas
        return 9999