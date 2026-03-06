from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Game
from django.views import View
from django.http import JsonResponse

class HomeView(View):
    def get(self, request):
        return JsonResponse({"status": "Casino API running"})
    
# Remove BetCreateView and the import line

class GameListView(ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"

class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"