from django.urls import path
from .interface.views import PlaceBetView
from .views import HomeView, GameListView, GameDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('place-bet/', PlaceBetView.as_view(), name='place_bet'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
]