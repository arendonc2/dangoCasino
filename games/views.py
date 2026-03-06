from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Game

class HomeView(View):
    def get(self, request):
        return render(request, 'games/home.html')

class GameListView(ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"

class GameDetailView(DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"