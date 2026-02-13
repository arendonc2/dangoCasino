from django.shortcuts import render

# Create your views here.

from django.views.generic import ListView, DetailView
from .models import Game

class GameListView(ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"

class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"
