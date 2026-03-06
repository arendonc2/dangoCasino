import os

class PrizeCalculatorFactory:

    @staticmethod
    def create(player):
        mode = os.getenv("PRIZE_CALCULATOR_MODE", "REAL")

        if mode == "MOCK":
            from infrastructure.services.mock_prize_calculator import MockPrizeCalculator
            return MockPrizeCalculator()

        # REAL
        if getattr(player, "is_vip", False):
            from infrastructure.services.vip_prize_calculator import VIPPrizeCalculator
            return VIPPrizeCalculator()

        from infrastructure.services.basic_prize_calculator import BasicPrizeCalculator
        return BasicPrizeCalculator()