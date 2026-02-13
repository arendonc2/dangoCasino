# domain/builders/bet_builder.py

class BetBuilder:
    def __init__(self):
        self._player = None
        self._game = None
        self._amount = None

    def with_player(self, player):
        if player is None:
            raise ValueError("El jugador es obligatorio")
        self._player = player
        return self

    def with_game(self, game):
        if game is None:
            raise ValueError("El juego es obligatorio")
        self._game = game
        return self

    def with_amount(self, amount):
        if amount is None or float(amount) <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        self._amount = float(amount)
        return self

    def _validate(self):
        if not all([self._player, self._game, self._amount]):
            raise ValueError("Datos incompletos para crear la apuesta")

        if self._player.balance < self._amount:
            raise ValueError("Saldo insuficiente")

    def build(self):
        self._validate()

        # Import local para evitar dependencia fuerte
        from games.models import Bet

        return Bet(
            player=self._player,
            game=self._game,
            amount=self._amount
        )