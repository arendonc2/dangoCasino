from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db import transaction
import logging

from ..application.services import BetService, RouletteService, CurrencyRateService
from ..infrastructure.repositories import (
    DjangoBetRepository,
    DjangoRouletteRepository,
)
from ..infrastructure.clients.roulette_service_client import RouletteServiceClient
from ..infrastructure.clients.ally_service_client import AllyServiceClient
from ..infrastructure.adapters.currency_rate_adapter import CurrencyRateAdapter
from ..tasks import audit_roulette_play
from ..models import Player, Bet, RouletteBet
from ..session_utils import get_current_player

logger = logging.getLogger(__name__)

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}


def roulette_number_color(number):
    if number in RED_NUMBERS:
        return "red"
    if number in BLACK_NUMBERS:
        return "black"
    return "green"


class DjangoHealthView(View):
    def get(self, request):
        return JsonResponse({"status": "ok", "service": "django"})


class PlayerSummaryView(View):
    def get(self, request, player_id):
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return JsonResponse({
                "service": "django-casino",
                "status": "error",
                "message": _("Player not found"),
            }, status=404)
        except Exception:
            logger.exception("Unexpected error loading player summary")
            return JsonResponse({
                "service": "django-casino",
                "status": "error",
                "message": _("Unexpected server error"),
            }, status=500)

        roulette_bets = RouletteBet.objects.filter(player_id=player_id)
        total_roulette_bets = roulette_bets.count()
        total_regular_bets = Bet.objects.filter(player_id=player_id).count()
        total_wins = roulette_bets.filter(result="win").count()
        latest_bet = roulette_bets.order_by("-created_at").first()
        updated_at = latest_bet.created_at if latest_bet else timezone.now()

        return JsonResponse({
            "service": "django-casino",
            "player_id": player.id,
            "username": player.username,
            "balance": player.balance,
            "total_bets": total_regular_bets + total_roulette_bets,
            "total_wins": total_wins,
            "updated_at": updated_at.isoformat(),
        })


class AllyStatusView(View):
    def get(self, request):
        ally = AllyServiceClient().get_status()
        return JsonResponse({
            "service": "django-casino",
            "ally": ally,
        })


class CurrencyRateView(View):
    def get(self, request):
        service = CurrencyRateService(CurrencyRateAdapter())
        rate = service.get_cop_to_usd_rate()

        return JsonResponse({
            "service": "django-casino",
            "adapter": "currency-rate-adapter",
            "source": "mock_or_fallback",
            "base_currency": "COP",
            "target_currency": "USD",
            "rate": rate,
            "message": _("Currency rate obtained through adapter"),
        })


class SystemStatusView(View):
    def get(self, request):
        ally = AllyServiceClient().get_status()
        currency_rate = CurrencyRateService(CurrencyRateAdapter()).get_cop_to_usd_rate()

        context = {
            "ally": ally,
            "currency_rate": currency_rate,
            "health_django": "/health/django/",
            "health_flask": "/health/flask/",
            "ally_status_endpoint": "/api/v1/ally-status/",
            "currency_rate_endpoint": "/api/v1/currency-rate/",
            "player_summary_example": "/api/v1/player-summary/1/",
        }
        return render(request, "games/system_status.html", context)


class LoginView(View):
    def get(self, request):
        return render(request, "games/login.html", {
            "current_player": get_current_player(request),
        })

    def post(self, request):
        username = (request.POST.get("username") or "").strip()

        if not username:
            return render(request, "games/login.html", {
                "error": "Ingresa tu nombre de usuario para iniciar sesión.",
                "current_player": get_current_player(request),
            })

        player = Player.objects.filter(username=username).first()
        if not player:
            return render(request, "games/login.html", {
                "error": "No encontramos ese usuario. Puedes crear una cuenta nueva.",
                "current_player": get_current_player(request),
            })

        request.session["player_id"] = player.id
        request.session["player_username"] = player.username
        messages.success(request, f"Bienvenido, {player.username}.")
        return redirect("play_roulette")


class LogoutView(View):
    def post(self, request):
        request.session.pop("player_id", None)
        request.session.pop("player_username", None)
        messages.success(request, "Tu sesión se cerró correctamente.")
        return redirect("home")

class RegisterView(View):
    def get(self, request):
        return render(request, 'games/register.html', {
            'current_player': get_current_player(request),
        })

    def post(self, request):
        username = (request.POST.get('username') or '').strip()

        if not username:
            return render(request, 'games/register.html', {
                'error': "El nombre de usuario es obligatorio.",
                'current_player': get_current_player(request),
            })

        try:
            balance = float(request.POST.get('balance', 1000.0))
        except (TypeError, ValueError):
            return render(request, 'games/register.html', {
                'error': "El saldo inicial debe ser un número válido.",
                'current_player': get_current_player(request),
            })

        if balance < 0:
            return render(request, 'games/register.html', {
                'error': "El saldo inicial no puede ser negativo.",
                'current_player': get_current_player(request),
            })

        if Player.objects.filter(username=username).exists():
            return render(request, 'games/register.html', {
                'error': "Ese nombre de usuario ya existe.",
                'current_player': get_current_player(request),
            })

        player = Player.objects.create(username=username, balance=balance, is_vip=False)
        request.session["player_id"] = player.id
        request.session["player_username"] = player.username
        messages.success(request, f"Cuenta creada con éxito. Bienvenido, {player.username}.")
        return redirect('play_roulette')

class PlaceBetView(View):
    def post(self, request):
        user_id = int(request.POST.get('user_id'))
        amount = float(request.POST.get('amount'))
        game_type = request.POST.get('game_type')
        user_type = request.POST.get('user_type')
        
        service = BetService(DjangoBetRepository())
        result = service.place_bet_and_calculate_prize(user_id, amount, game_type, user_type)
        
        return JsonResponse(result)

@method_decorator(csrf_exempt, name='dispatch')
class RouletteView(View):
    def get(self, request):
        current_player = get_current_player(request)
        if not current_player:
            messages.error(request, "Para jugar, primero inicia sesión o crea una cuenta.")
            return redirect("login")
        return render(request, 'games/roulette.html', {
            'current_player': current_player,
        })

    def post(self, request):
        current_player = get_current_player(request)
        if not current_player:
            if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                return JsonResponse({
                    "message": "Para jugar, primero inicia sesión o crea una cuenta.",
                }, status=401)
            messages.error(request, "Para jugar, primero inicia sesión o crea una cuenta.")
            return redirect("login")

        user_id = current_player.id

        bet_type = (request.POST.get('bet_type') or '').strip()
        bet_value = (request.POST.get('bet_value') or '').strip().lower()

        try:
            amount = float(request.POST.get('amount'))
        except (TypeError, ValueError):
            amount = None

        validation_error = None

        if not bet_type or not bet_value:
            validation_error = "Selecciona una apuesta en el tablero antes de girar la ruleta."
        elif bet_type not in ('number', 'color', 'odd_even'):
            validation_error = "La apuesta seleccionada no es válida."
        elif amount is None or amount <= 0:
            validation_error = "Ingresa un monto válido mayor a 0."
        elif amount > current_player.balance:
            validation_error = "No tienes saldo suficiente para realizar esta apuesta."
        elif bet_type == 'number':
            try:
                number_value = int(bet_value)
            except ValueError:
                number_value = None

            if number_value is None or number_value < 0 or number_value > 36:
                validation_error = "El número debe estar entre 0 y 36."
            else:
                bet_value = str(number_value)
        elif bet_type == 'color' and bet_value not in ('red', 'black'):
            validation_error = "El color seleccionado no es válido."
        elif bet_type == 'odd_even' and bet_value not in ('odd', 'even'):
            validation_error = "La opción seleccionada no es válida."

        if validation_error:
            result = {
                'spun_number': None,
                'win': False,
                'payout': 0,
                'message': validation_error,
            }
            if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                return JsonResponse(result, status=400)
            return render(request, 'games/roulette.html', {
                'result': result,
                'current_player': current_player,
            })

        payload = {
            "player_id": user_id,
            "bet_type": bet_type,
            "bet_value": bet_value,
            "amount": amount,
        }

        with transaction.atomic():
            locked_player = get_current_player(request, for_update=True)
            if not locked_player:
                if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                    return JsonResponse({
                        "message": "Tu sesión no es válida. Inicia sesión nuevamente.",
                    }, status=401)
                messages.error(request, "Tu sesión no es válida. Inicia sesión nuevamente.")
                return redirect("login")

            if amount > locked_player.balance:
                result = {
                    'spun_number': None,
                    'win': False,
                    'payout': 0,
                    'message': "No tienes saldo suficiente para realizar esta apuesta.",
                }
                if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
                    return JsonResponse(result, status=400)
                return render(request, 'games/roulette.html', {
                    'result': result,
                    'current_player': locked_player,
                })

            balance_before = locked_player.balance

            client = RouletteServiceClient()
            response = client.play_roulette(payload)

            if response.get("ok"):
                flask_data = response["data"]
                result = {
                    'spun_number': flask_data.get('winning_number'),
                    'win': flask_data.get('is_winner', False),
                    'payout': flask_data.get('payout', 0),
                    'winning_color': flask_data.get('color'),
                    'source': flask_data.get('service', 'flask-roulette'),
                    'message': 'Tu jugada fue procesada correctamente.',
                }

                DjangoRouletteRepository().save_roulette_bet({
                    'player_id': user_id,
                    'bet_type': bet_type,
                    'bet_value': str(bet_value),
                    'amount': amount,
                    'result': 'win' if result['win'] else 'lose',
                    'spun_number': result['spun_number'],
                    'payout': result['payout'],
                })
            else:
                logger.warning("Roulette microservice failed, activating fallback: %s", response)
                service = RouletteService(DjangoRouletteRepository())
                result = service.play_roulette(user_id, bet_type, bet_value, amount)
                result['winning_color'] = roulette_number_color(result.get('spun_number'))
                result['source'] = 'django-fallback'
                result['message'] = "Tuvimos una intermitencia temporal, pero tu jugada fue procesada correctamente."

            balance_after = balance_before - amount + result.get('payout', 0)
            if balance_after < 0:
                balance_after = 0

            locked_player.balance = balance_after
            locked_player.save(update_fields=['balance'])

            result['amount'] = amount
            result['balance_before'] = balance_before
            result['balance_after'] = balance_after

        audit_payload = {
            "player_id": user_id,
            "bet_type": bet_type,
            "bet_value": bet_value,
            "amount": amount,
            "winning_number": result.get("spun_number"),
            "is_winner": result.get("win"),
            "payout": result.get("payout"),
            "source": result.get("source"),
        }

        try:
            audit_roulette_play.delay(audit_payload)
        except Exception:
            logger.exception("Could not dispatch roulette audit task")
            result['system_notice'] = "Tu jugada quedó registrada correctamente."

        current_player = get_current_player(request)

        if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
            result['current_balance'] = current_player.balance if current_player else None
            return JsonResponse(result)

        return render(request, 'games/roulette.html', {
            'result': result,
            'current_player': current_player,
        })