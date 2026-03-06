from ..services.prize_calculator import PrizeCalculator
from ..services.vip_prize_calculator import VIPPrizeCalculator
from ..services.basic_prize_calculator import BasicPrizeCalculator

class PrizeCalculatorFactory:
    @staticmethod
    def create_calculator(user_type: str) -> PrizeCalculator:
        if user_type == "VIP":
            return VIPPrizeCalculator()
        else:
            return BasicPrizeCalculator()