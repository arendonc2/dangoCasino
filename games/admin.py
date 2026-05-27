from django.contrib import admin

from .models import Bet, Game, Player, RouletteBet


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "balance", "is_vip")
	search_fields = ("username",)
	list_filter = ("is_vip",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
	list_display = ("id", "player", "game", "amount", "potential_prize", "created_at")
	list_filter = ("game", "created_at")
	search_fields = ("player__username",)


@admin.register(RouletteBet)
class RouletteBetAdmin(admin.ModelAdmin):
	list_display = ("id", "player", "bet_type", "bet_value", "amount", "result", "spun_number", "payout", "created_at")
	list_filter = ("bet_type", "result", "created_at")
	search_fields = ("player__username", "bet_value")
