from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import asyncio
import json
from .pong import PongGame  # Assumendo che la classe PongGame sia in un file separato
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    games = {}  # Dizionario condiviso per memorizzare le istanze del gioco per ogni `game_id`

    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = f"game_{self.game_id}"
        self.player_side = None  # Sarà assegnato come "left" o "right" dopo l'autenticazione
        self.user = None  # Utente autenticato
        self.game = None  # Istanza del gioco

        # Accetta la connessione WebSocket per ricevere il token
        await self.accept()

    async def receive(self, text_data):
        """
        Gestisce i messaggi ricevuti dal WebSocket.
        """
        # Se l'utente non è autenticato, prova a autenticare con il primo messaggio
        if not self.user:
            token = text_data.strip()
            self.user = await self.authenticate_user(token)
            if self.user is None:
                await self.send_json({"error": "Authentication failed. Closing connection."})
                await self.close(code=4001)  # Codice di errore personalizzato
                return

            # Aggiungi l'utente autenticato alla stanza
            await self.join_game()
            return
        
        print(f"Received message from {self.user}: {text_data}")
        # Elabora i dati inviati dal client
        try:
            input_data = json.loads(text_data)
        except json.JSONDecodeError:
            return


        await self.game.process_input(self.player_side, input_data)

    async def disconnect(self, close_code):
        """
        Gestisce la disconnessione del client.
        """
        # Rimuovi l'utente dalla stanza
        await self.leave_game()

    async def authenticate_user(self, token):
        """
        Autentica l'utente utilizzando il token JWT fornito.
        """
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = await database_sync_to_async(jwt_auth.get_user)(validated_token)
            return user
        except AuthenticationFailed:
            return None

    async def join_game(self):
        """
        Aggiunge l'utente autenticato alla stanza e assegna un lato del campo.
        """
        # Aggiungi l'utente al gruppo del canale
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # Crea una nuova istanza del gioco se non esiste
        if self.game_id not in GameConsumer.games:
            GameConsumer.games[self.game_id] = PongGame(self.game_id)
        self.game = GameConsumer.games[self.game_id]

        # Assegna un lato al giocatore
        game = GameConsumer.games[self.game_id]
        if len(game.clients) == 0:
            self.player_side = "left"
        elif len(game.clients) == 1:
            self.player_side = "right"
        else:
            await self.send_json({"error": "Game room is full. Closing connection."})
            await self.close()
            return

        # Aggiungi il client alla lista dei giocatori
        game.clients.append(self)
        await self.send_json({"message": "Authentication successful. Welcome to the game!", "player_side": self.player_side})

        # Avvia il game loop se entrambi i giocatori sono connessi
        if len(game.clients) == 2:
            asyncio.create_task(self.game_loop())


    async def leave_game(self):
        """
        Rimuove l'utente dalla stanza e aggiorna lo stato del gioco.
        """
        # Rimuovi il client dal gruppo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        # Rimuovi il client dall'istanza del gioco
        game = GameConsumer.games.get(self.game_id)
        if game:
            game.clients.remove(self)
            if not game.clients:  # Se non ci sono più client, elimina l'istanza del gioco
                del GameConsumer.games[self.game_id]

    async def game_loop(self):
        """
        Aggiorna periodicamente lo stato del gioco e lo trasmette ai client.
        """
        game = GameConsumer.games.get(self.game_id)
        if not game:
            return

        while game.clients:  # Esegui il ciclo finché ci sono client connessi
            await game.update_game_state()
            await game.broadcast_state()
            await asyncio.sleep(1 / 60)  # Ciclo a 60 FPS

    async def send_json(self, content):
        """
        Funzione helper per inviare messaggi JSON al WebSocket.
        """
        await self.send(text_data=json.dumps(content))