from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Game
from .session_utils import get_current_player

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