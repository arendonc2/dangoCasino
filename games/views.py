from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Game, Player, Deposit
from .session_utils import get_current_player
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.contrib import messages

class HomeView(View):
    def get(self, request):
        current_player = get_current_player(request)
        return render(request, 'games/home.html', {
            'current_player': current_player,
        })

class GameListView(ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_player"] = get_current_player(self.request)
        return context

class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_player"] = get_current_player(self.request)
        return context
    
class DepositView(View):
    TEMPLATE = "games/deposit.html"
    MIN_DEPOSIT = Decimal("1000")       # monto mínimo en COP
    MAX_DEPOSIT = Decimal("10000000")   # monto máximo en COP
    QUICK_AMOUNTS = [10_000, 50_000, 100_000, 500_000, 1_000_000]
 
    def _get_player(self, request, for_update=False):
        player_id = request.session.get("player_id")
        if not player_id:
            return None
        qs = Player.objects.filter(id=player_id)
        if for_update:
            qs = qs.select_for_update()
        return qs.first()
 
    def get(self, request):
        player = self._get_player(request)
        if not player:
            return redirect("login")
        
        return render(request, self.TEMPLATE, {
            "player": player,
            "quick_amounts": self.QUICK_AMOUNTS,
            "min_deposit": self.MIN_DEPOSIT,
            "max_deposit": self.MAX_DEPOSIT,
        })
 
    def post(self, request):
        player = self._get_player(request)
        if not player:
            return redirect("login")
 
        # --- 1. Parsear monto ---
        raw_amount = request.POST.get("amount", "").strip()
        try:
            amount = Decimal(raw_amount)
        except InvalidOperation:
            messages.error(request, "El monto ingresado no es válido.")
            return redirect("deposit")
 
        # --- 2. Validaciones de negocio ---
        if amount < self.MIN_DEPOSIT:
            messages.error(
                request,
                f"El monto mínimo de recarga es ${self.MIN_DEPOSIT:,.0f} COP."
            )
            return redirect("deposit")
 
        if amount > self.MAX_DEPOSIT:
            messages.error(
                request,
                f"El monto máximo de recarga es ${self.MAX_DEPOSIT:,.0f} COP."
            )
            return redirect("deposit")
 
        # --- 3. Transacción atómica con lock ---
        try:
            with transaction.atomic():
                # Re-leer jugador con lock para evitar concurrencia
                player = self._get_player(request, for_update=True)
                if not player:
                    raise ValueError("Jugador no encontrado.")
 
                balance_before = player.balance
                player.balance += amount
                balance_after = player.balance
                player.save(update_fields=["balance"])
 
                # Persistir depósito
                from .models import Deposit  # ajusta el import
                deposit = Deposit.objects.create(
                    player=player,
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status="confirmed",
                )
 
        except Exception as e:
            messages.error(
                request,
                "Ocurrió un error procesando la recarga. Intenta de nuevo."
            )
            return redirect("deposit")
 
        # --- 4. Auditoría asíncrona (opcional, no bloquea si falla) ---
        try:
            from .tasks import audit_deposit
            audit_deposit.delay(deposit.id)
        except Exception:
            pass
 
        # --- 5. Respuesta exitosa ---
        messages.success(
            request,
            f"¡Recarga exitosa! Se acreditaron ${amount:,.0f} COP a tu cuenta. "
            f"Saldo actual: ${balance_after:,.0f} COP."
        )
        return redirect("roulette")  # ajusta al nombre de tu URL de ruleta