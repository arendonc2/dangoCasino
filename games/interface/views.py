from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..application.services import BetService, RouletteService
from ..infrastructure.repositories import (
    DjangoBetRepository,
    DjangoRouletteRepository,
)
from ..models import Player

class LoginView(View):
    def get(self, request):
        # Si ya tiene sesión activa, redirigir a ruleta
        if request.session.get('player_id'):
            return redirect('play_roulette')
        return render(request, 'games/login.html')

    def post(self, request):
        username = request.POST.get('username')
        
        try:
            player = Player.objects.get(username=username)
            
            # Guardar sesión
            request.session['player_id'] = player.id
            request.session['username'] = player.username
            
            return redirect('play_roulette')
        except Player.DoesNotExist:
            return render(request, 'games/login.html', {
                'error': 'Username not found. Please register first.'
            })


class RegisterView(View):
    def get(self, request):
        # Si ya tiene sesión activa, redirigir a ruleta
        if request.session.get('player_id'):
            return redirect('play_roulette')
        return render(request, 'games/register.html')

    def post(self, request):
        username = request.POST.get('username')
        balance = float(request.POST.get('balance', 1000.0))

        if Player.objects.filter(username=username).exists():
            return render(request, 'games/register.html', {
                'error': 'Username already exists.'
            })

        player = Player.objects.create(username=username, balance=balance, is_vip=False)
        
        # Guardar sesión
        request.session['player_id'] = player.id
        request.session['username'] = player.username
        
        return redirect('play_roulette')


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        return redirect('home')


class PlaceBetView(View):
    def post(self, request):
        user_id = int(request.POST.get('user_id'))
        amount = float(request.POST.get('amount'))
        game_type = request.POST.get('game_type')
        user_type = request.POST.get('user_type')
        
        service = BetService(DjangoBetRepository())
        result = service.place_bet_and_calculate_prize(user_id, amount, game_type, user_type)
        
        return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class RouletteView(View):
    def get(self, request):
        player_id = request.session.get('player_id')
        
        if not player_id:
            return redirect('register')
        
        try:
            player = Player.objects.get(id=player_id)
            context = {
                'player': player
            }
            return render(request, 'games/roulette.html', context)
        except Player.DoesNotExist:
            request.session.flush()
            return redirect('register')

    def post(self, request):
        player_id = request.session.get('player_id')
        
        if not player_id:
            return redirect('register')
        
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            request.session.flush()
            return redirect('register')
        
        bet_type = request.POST.get('bet_type')
        bet_value = request.POST.get('bet_value')
        amount = float(request.POST.get('amount'))

        service = RouletteService(DjangoRouletteRepository())
        result = service.play_roulette(player_id, bet_type, bet_value, amount)

        if request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
            return JsonResponse(result)

        context = {
            'result': result,
            'player': player
        }
        return render(request, 'games/roulette.html', context)