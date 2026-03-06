from django.views import View
from django.http import JsonResponse
from ..application.services import BetService
from ..infrastructure.repositories import DjangoBetRepository

class PlaceBetView(View):
    def post(self, request):
        user_id = int(request.POST.get('user_id'))
        amount = float(request.POST.get('amount'))
        game_type = request.POST.get('game_type')
        user_type = request.POST.get('user_type')
        
        service = BetService(DjangoBetRepository())
        result = service.place_bet_and_calculate_prize(user_id, amount, game_type, user_type)
        
        return JsonResponse(result)