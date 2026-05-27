"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from games.views import HomeView
from games.interface.views import (
    DjangoHealthView,
    PlayerSummaryView,
    AllyStatusView,
    CurrencyRateView,
)
urlpatterns = [
    path("", HomeView.as_view()),
    path("i18n/", include("django.conf.urls.i18n")),
    path("health/django/", DjangoHealthView.as_view(), name="health_django"),
    path("api/v1/player-summary/<int:player_id>/", PlayerSummaryView.as_view(), name="player_summary"),
    path("api/v1/ally-status/", AllyStatusView.as_view(), name="ally_status"),
    path("api/v1/currency-rate/", CurrencyRateView.as_view(), name="currency_rate"),
    path('admin/', admin.site.urls),
    path("games/", include("games.urls")),
]
