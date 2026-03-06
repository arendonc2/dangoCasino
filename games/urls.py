from django.urls import path
from .interface.views import PlaceBetView, RegisterView, RouletteView
from .views import HomeView, GameListView, GameDetailView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('place-bet/', PlaceBetView.as_view(), name='place_bet'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('play-roulette/', RouletteView.as_view(), name='play_roulette'),
]