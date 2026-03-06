from django.db import models


class Player(models.Model):
    username = models.CharField(max_length=100)
    balance = models.FloatField(default=0)
    is_vip = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Bet(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    amount = models.FloatField()
    potential_prize = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bet #{self.id} - {self.player}"
    

class RouletteBet(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    bet_type = models.CharField(max_length=20)  # 'number' or 'color'
    bet_value = models.CharField(max_length=10)  # e.g., '5' or 'red'
    amount = models.FloatField()
    result = models.CharField(max_length=20, blank=True)  # 'win' or 'lose'
    spun_number = models.IntegerField(null=True)
    payout = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Roulette Bet #{self.id} - {self.player}"