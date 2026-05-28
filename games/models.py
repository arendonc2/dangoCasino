from django.db import models
from django.utils import timezone

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
    
class Deposit(models.Model):
    """
    Registra cada recarga de saldo que hace un jugador.
    Se integra al flujo existente de Player y RouletteBet.
    """
 
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("confirmed", "Confirmado"),
        ("failed", "Fallido"),
    ]
 
    player = models.ForeignKey(
        "Player",
        on_delete=models.CASCADE,
        related_name="deposits",
        verbose_name="Jugador",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto recargado",
    )
    balance_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Saldo antes",
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Saldo después",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="confirmed",
        verbose_name="Estado",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de recarga",
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notas internas",
    )
 
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Depósito"
        verbose_name_plural = "Depósitos"
 
    def __str__(self):
        return f"Depósito #{self.id} | {self.player} | +{self.amount}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("approved", "Pago simulado aprobado"),
        ("confirmed", "Orden confirmada"),
        ("failed", "Fallida"),
    ]

    player = models.ForeignKey(
        "Player",
        on_delete=models.CASCADE,
        related_name="purchase_orders",
        verbose_name="Comprador",
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de compra")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Orden de compra"
        verbose_name_plural = "Ordenes de compra"

    @property
    def order_code(self):
        return f"ORD-{self.id:06d}"

    def __str__(self):
        return f"{self.order_code} - {self.player}"


class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Orden",
    )
    product_name = models.CharField(max_length=120, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal")

    class Meta:
        verbose_name = "Item de orden"
        verbose_name_plural = "Items de orden"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"