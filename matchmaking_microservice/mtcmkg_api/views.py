import uuid
from threading import Condition
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

conditions = {}

def get_condition(password):
    if password not in conditions:
        conditions[password] = Condition()
    return conditions[password]

class PongPrivatePasswordMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password")
        username = request.user.username
        if not password:
            return Response({"detail": "Password is required"}, status=400)

        game_id_key = f"game_id_{password}"

        if cache.get(game_id_key) and username == cache.get(game_id_key).get("username"):
            condition = get_condition(password)
            with condition:
                condition.notify()
                condition.wait(timeout=1)

        if cache.get(game_id_key):  # Giocatore 2 trova il game_id
            game_id = cache.get(game_id_key)
            cache.delete(game_id_key)
            with get_condition(password):
                get_condition(password).notify()
            return Response({"game_id": game_id}, status=200)

        # Giocatore 1 crea una condizione e aspetta
        condition = get_condition(password)
        with condition:
            game_id = str(uuid.uuid4())
            cache.set(game_id_key, {"game_id": game_id, "username": username})
            condition.wait(timeout=60)
        if not cache.get(game_id_key):
            return Response({"game_id": game_id}, status=200)
        
        cache.delete(game_id_key)
        return Response({"detail": "Game not found"}, status=404)


