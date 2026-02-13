# domain/factories/prize_calculator_factory.py

class PrizeCalculatorFactory:

    @staticmethod
    def create(player):
        if getattr(player, "is_vip", False):
            from infrastructure.services.vip_prize_calculator import VIPPrizeCalculator
            return VIPPrizeCalculator()

        from infrastructure.services.basic_prize_calculator import BasicPrizeCalculator
        return BasicPrizeCalculator()