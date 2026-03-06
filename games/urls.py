from django.urls import path
from .interface.views import RegisterView, RouletteView, LogoutView, LoginView
from .views import HomeView, GameListView, GameDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('play-roulette/', RouletteView.as_view(), name='play_roulette'),
]