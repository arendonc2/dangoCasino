from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse

from .forms import LoginForm, RegisterForm, RoulettePlayForm
from ..application.services import BetService, RouletteService, AuthService
from ..infrastructure.repositories import (
    DjangoBetRepository,
    DjangoRouletteRepository,
    DjangoPlayerRepository,
)

class LoginView(View):
    def get(self, request):
        if request.session.get("player_id"):
            return redirect("play_roulette")
        return render(request, "games/login.html", {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, "games/login.html", {"form": form})

        auth_service = AuthService(DjangoPlayerRepository())
        try:
            player = auth_service.login(form.cleaned_data["username"])
            request.session["player_id"] = player.id
            request.session["username"] = player.username
            return redirect("play_roulette")
        except ValueError as e:
            return render(request, "games/login.html", {"form": form, "error": str(e)})


class RegisterView(View):
    def get(self, request):
        if request.session.get("player_id"):
            return redirect("play_roulette")
        return render(request, "games/register.html", {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return render(request, "games/register.html", {"form": form})

        auth_service = AuthService(DjangoPlayerRepository())
        try:
            player = auth_service.register(
                username=form.cleaned_data["username"],
                balance=form.cleaned_data["balance"],
            )
            request.session["player_id"] = player.id
            request.session["username"] = player.username
            return redirect("play_roulette")
        except ValueError as e:
            return render(request, "games/register.html", {"form": form, "error": str(e)})


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect("home")


class RouletteView(View):
    def get(self, request):
        player_id = request.session.get("player_id")
        if not player_id:
            return redirect("login")

        auth_service = AuthService(DjangoPlayerRepository())
        try:
            player = auth_service.get_player(player_id)
            return render(request, "games/roulette.html", {"player": player, "form": RoulettePlayForm()})
        except ValueError:
            request.session.flush()
            return redirect("login")

    def post(self, request):
        player_id = request.session.get("player_id")
        if not player_id:
            return redirect("login")

        form = RoulettePlayForm(request.POST)
        auth_service = AuthService(DjangoPlayerRepository())
        if not form.is_valid():
            player = auth_service.get_player(player_id)
            return render(request, "games/roulette.html", {"player": player, "form": form})

        roulette_service = RouletteService(DjangoRouletteRepository())
        try:
            result = roulette_service.play_roulette(
                user_id=player_id,
                bet_type=form.cleaned_data["bet_type"],
                bet_value=form.cleaned_data["bet_value"],
                amount=float(form.cleaned_data["amount"]),
            )
            player = auth_service.get_player(player_id)  # recarga saldo actualizado

            if request.META.get("HTTP_ACCEPT", "").startswith("application/json"):
                return JsonResponse(result)

            return render(request, "games/roulette.html", {
                "player": player,
                "result": result,
                "form": RoulettePlayForm(),
            })
        except ValueError as e:
            player = auth_service.get_player(player_id)
            return render(request, "games/roulette.html", {
                "player": player,
                "form": form,
                "error": str(e),
            })