from .models import Player


def get_current_player(request, for_update=False):
    player_id = request.session.get("player_id")
    if not player_id:
        return None

    queryset = Player.objects
    if for_update:
        queryset = queryset.select_for_update()

    try:
        return queryset.get(id=player_id)
    except Player.DoesNotExist:
        request.session.pop("player_id", None)
        request.session.pop("player_username", None)
        return None
