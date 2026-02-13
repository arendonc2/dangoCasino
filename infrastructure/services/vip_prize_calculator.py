# infrastructure/services/vip_prize_calculator.py

from domain.services.prize_calculator import PrizeCalculator


class VIPPrizeCalculator(PrizeCalculator):

    def calculate(self, bet):
        # mejor multiplicador para VIP
        return bet.amount * 3