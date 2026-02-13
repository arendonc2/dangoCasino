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