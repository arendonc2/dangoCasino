from django.contrib import admin

from .models import Bet, Game, Player, RouletteBet, Deposit, PurchaseOrder, PurchaseOrderItem


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

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "amount",
        "balance_before",
        "balance_after",
        "status",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["player__username", "player__id"]
    readonly_fields = [
        "player",
        "amount",
        "balance_before",
        "balance_after",
        "created_at",
    ]
    ordering = ["-created_at"]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    readonly_fields = ("product_name", "quantity", "unit_price", "subtotal")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "status", "subtotal", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("player__username",)
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_name", "quantity", "unit_price", "subtotal")
    search_fields = ("product_name", "order__id", "order__player__username")