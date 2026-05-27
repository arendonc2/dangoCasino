from django.urls import path
from .interface.views import PlaceBetView, RegisterView, RouletteView, SystemStatusView, LoginView, LogoutView
from .views import HomeView, GameListView, GameDetailView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('place-bet/', PlaceBetView.as_view(), name='place_bet'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('play-roulette/', RouletteView.as_view(), name='play_roulette'),
    path('system-status/', SystemStatusView.as_view(), name='system_status'),
]