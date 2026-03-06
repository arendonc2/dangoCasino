import random

class RouletteRules:
    RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19,
                   21, 23, 25, 27, 30, 32, 34, 36]
    BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20,
                     22, 24, 26, 28, 29, 31, 33, 35]

    @staticmethod
    def spin_wheel():
        return random.randint(1, 36)           # no zero

    @staticmethod
    def check_win(bet_type, bet_value, spun_number):
        if bet_type == 'number':
            return str(spun_number) == bet_value
        elif bet_type == 'color':
            if bet_value == 'red' and spun_number in RouletteRules.RED_NUMBERS:
                return True
            if bet_value == 'black' and spun_number in RouletteRules.BLACK_NUMBERS:
                return True
            if bet_value == 'green' and spun_number == 0:
                return True
        elif bet_type == 'odd_even':
            if bet_value == 'odd' and spun_number % 2 == 1:
                return True
            if bet_value == 'even' and spun_number % 2 == 0:
                return True
        return False

    @staticmethod
    def calculate_payout(bet_type, amount):
        if bet_type == 'number':
            return amount * 35
        elif bet_type in ('color', 'odd_even'):
            return amount * 2
        return 0