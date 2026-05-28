from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Game, Deposit, PurchaseOrder, PurchaseOrderItem
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
    CART_SESSION_KEY = "checkout_cart"
    PRODUCT_CATALOG = [
        {"sku": "chips-10k", "name": "Pack de fichas 10.000", "unit_price": Decimal("10000")},
        {"sku": "chips-50k", "name": "Pack de fichas 50.000", "unit_price": Decimal("50000")},
        {"sku": "chips-100k", "name": "Pack de fichas 100.000", "unit_price": Decimal("100000")},
        {"sku": "chips-500k", "name": "Pack VIP 500.000", "unit_price": Decimal("500000")},
        {"sku": "chips-1m", "name": "Pack Black 1.000.000", "unit_price": Decimal("1000000")},
    ]

    def _catalog_index(self):
        return {item["sku"]: item for item in self.PRODUCT_CATALOG}

    def _get_player(self, request, for_update=False):
        return get_current_player(request, for_update=for_update)

    def _get_cart(self, request):
        raw = request.session.get(self.CART_SESSION_KEY, [])
        return raw if isinstance(raw, list) else []

    def _save_cart(self, request, cart):
        request.session[self.CART_SESSION_KEY] = cart
        request.session.modified = True

    def _cart_totals(self, cart):
        subtotal = Decimal("0")
        for item in cart:
            item_subtotal = Decimal(str(item.get("subtotal", "0")))
            subtotal += item_subtotal

        discount = Decimal("0")
        tax = Decimal("0")
        shipping = Decimal("0")
        total = subtotal - discount + tax + shipping

        return {
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "shipping": shipping,
            "total": total,
        }

    def _validated_checkout_items(self, cart):
        validated = []
        for item in cart:
            name = (item.get("name") or "").strip()
            if not name:
                raise ValueError("Hay un producto sin nombre en el carrito.")

            quantity = int(item.get("quantity", 0))
            if quantity <= 0:
                raise ValueError("Hay productos con cantidad invalida en el carrito.")

            unit_price = Decimal(str(item.get("unit_price", "0")))
            subtotal = Decimal(str(item.get("subtotal", "0")))

            if unit_price <= 0 or subtotal <= 0:
                raise ValueError("Hay productos con precio invalido en el carrito.")

            validated.append({
                "sku": item.get("sku", "custom"),
                "name": name,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        return validated

    def get(self, request):
        player = self._get_player(request)
        if not player:
            return redirect("login")

        cart = self._get_cart(request)
        totals = self._cart_totals(cart)

        return render(request, self.TEMPLATE, {
            "player": player,
            "products": self.PRODUCT_CATALOG,
            "cart_items": cart,
            "totals": totals,
        })

    def post(self, request):
        player = self._get_player(request)
        if not player:
            return redirect("login")

        action = (request.POST.get("action") or "").strip().lower()
        if action == "add":
            return self._add_to_cart(request)
        if action == "remove":
            return self._remove_from_cart(request)
        if action == "checkout":
            return self._checkout(request)

        messages.error(request, "Accion de carrito no valida.")
        return redirect("deposit")

    def _add_to_cart(self, request):
        cart = self._get_cart(request)
        catalog = self._catalog_index()

        sku = (request.POST.get("sku") or "").strip()
        quantity_raw = (request.POST.get("quantity") or "1").strip()

        try:
            quantity = int(quantity_raw)
        except ValueError:
            messages.error(request, "La cantidad ingresada no es valida.")
            return redirect("deposit")

        if quantity <= 0:
            messages.error(request, "La cantidad debe ser mayor a 0.")
            return redirect("deposit")

        if not sku or sku not in catalog:
            messages.error(request, "Solo puedes agregar productos del catalogo de fichas.")
            return redirect("deposit")

        product = catalog[sku]
        product_name = product["name"]
        unit_price = Decimal(product["unit_price"])

        if unit_price <= 0:
            messages.error(request, "El precio del producto no es valido.")
            return redirect("deposit")

        existing = next((item for item in cart if item.get("sku") == sku and Decimal(str(item.get("unit_price", "0"))) == unit_price), None)
        if existing:
            existing["quantity"] = int(existing.get("quantity", 0)) + quantity
            existing_subtotal = Decimal(str(existing.get("unit_price", "0"))) * Decimal(existing["quantity"])
            existing["subtotal"] = str(existing_subtotal)
        else:
            subtotal = unit_price * Decimal(quantity)
            cart.append({
                "sku": sku,
                "name": product_name,
                "quantity": quantity,
                "unit_price": str(unit_price),
                "subtotal": str(subtotal),
            })

        self._save_cart(request, cart)
        messages.success(request, f"{product_name} agregado al carrito.")
        return redirect("deposit")

    def _remove_from_cart(self, request):
        cart = self._get_cart(request)
        sku = (request.POST.get("sku") or "").strip()
        if not sku:
            messages.error(request, "No se pudo identificar el producto a remover.")
            return redirect("deposit")

        new_cart = [item for item in cart if item.get("sku") != sku]
        if len(new_cart) == len(cart):
            messages.error(request, "El producto ya no estaba en el carrito.")
            return redirect("deposit")

        self._save_cart(request, new_cart)
        messages.success(request, "Producto eliminado del carrito.")
        return redirect("deposit")

    def _checkout(self, request):
        cart = self._get_cart(request)
        if not cart:
            messages.error(request, "Tu carrito esta vacio. Agrega productos antes de finalizar compra.")
            return redirect("deposit")

        try:
            items = self._validated_checkout_items(cart)
        except Exception as exc:
            messages.error(request, f"No se pudo procesar el carrito: {exc}")
            return redirect("deposit")

        totals = self._cart_totals(items)
        if totals["total"] <= 0:
            messages.error(request, "No se puede generar una orden con total 0.")
            return redirect("deposit")

        try:
            with transaction.atomic():
                player = self._get_player(request, for_update=True)
                if not player:
                    messages.error(request, "Tu sesion expiro. Inicia sesion nuevamente.")
                    return redirect("login")

                order = PurchaseOrder.objects.create(
                    player=player,
                    status="confirmed",
                    subtotal=totals["subtotal"],
                    discount=totals["discount"],
                    tax=totals["tax"],
                    shipping=totals["shipping"],
                    total=totals["total"],
                )

                for item in items:
                    PurchaseOrderItem.objects.create(
                        order=order,
                        product_name=item["name"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        subtotal=item["subtotal"],
                    )

                balance_before = Decimal(str(player.balance))
                balance_after = balance_before + totals["total"]
                player.balance = float(balance_after)
                player.save(update_fields=["balance"])

                deposit = Deposit.objects.create(
                    player=player,
                    amount=totals["total"],
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status="confirmed",
                    notes=f"Recarga por orden {order.order_code}",
                )
        except Exception:
            messages.error(request, "No pudimos confirmar la compra. Tu carrito sigue intacto.")
            return redirect("deposit")

        try:
            from .tasks import audit_deposit
            audit_deposit.delay(deposit.id)
        except Exception:
            pass

        self._save_cart(request, [])
        messages.success(request, "Compra realizada con exito. Tu pago simulado fue aprobado.")
        return redirect("checkout_success", order_id=order.id)


class CheckoutSuccessView(View):
    TEMPLATE = "games/checkout_success.html"

    def get(self, request, order_id):
        player = get_current_player(request)
        if not player:
            return redirect("login")

        order = get_object_or_404(
            PurchaseOrder.objects.prefetch_related("items"),
            id=order_id,
            player=player,
        )

        return render(request, self.TEMPLATE, {
            "current_player": player,
            "order": order,
            "items": order.items.all(),
        })