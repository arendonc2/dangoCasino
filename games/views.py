from django.shortcuts import render

# Create your views here.

from django.views.generic import ListView, DetailView
from .models import Game
from django.views import View
from django.http import JsonResponse
from application.services import create_bet

class HomeView(View):
    def get(self, request):
        return JsonResponse({"status": "Casino API running"})
    
class BetCreateView(View):

    def post(self, request):
        player_id = request.POST.get("player_id")
        game_id = request.POST.get("game_id")
        amount = request.POST.get("amount")

        bet = create_bet(player_id, game_id, amount)

        return JsonResponse({
            "bet_id": bet.id,
            "potential_prize": bet.potential_prize
        })
    
class GameListView(ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"

class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"
