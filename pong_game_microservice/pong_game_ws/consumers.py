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
        if hasattr(self.game, 'left_player') and self.game.left_player == self.user:
            self.player_side = "left"
        elif hasattr(self.game, 'right_player') and self.game.right_player == self.user:
            self.player_side = "right"
        elif len(self.game.clients) == 0:
            self.player_side = "left"
            self.game.left_player = self.user
        elif len(self.game.clients) == 1:
            self.player_side = "right"
            self.game.right_player = self.user
        else:
            await self.send_json({"error": "Game room is full. Closing connection."})
            await self.close()
            return

        # Aggiungi il client alla lista dei giocatori se non è già presente
        if self not in self.game.clients:
            self.game.clients.append(self)
        await self.send_json({
            "message": "Authentication successful. Welcome to the game!",
            "player_side": self.player_side,
        })

        # Invia un messaggio a tutti i client nel gruppo con i dettagli dei giocatori
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "players_update",
                "pippo": "player_update",
                "left_player": self.game.left_player.username if self.game.left_player else None,
                "left_player_trophies": self.game.left_player.trophies if self.game.left_player else None,
                "right_player": self.game.right_player.username if self.game.right_player else None,
                "right_player_trophies": self.game.right_player.trophies if self.game.right_player else None,
            }
        )

        # Avvia il game loop se non è già in esecuzione e entrambi i giocatori sono connessi
        if len(self.game.clients) == 2 and not self.game.game_loop_running:
            self.game.game_loop_running = True
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
            if self in game.clients:
                game.clients.remove(self)
            if not game.clients:  # Se non ci sono più client, elimina l'istanza del gioco
                await asyncio.sleep(5)  # Attendere 5 secondi prima di eliminare il gioco
                del GameConsumer.games[self.game_id]

    async def game_loop(self):
        """
        Aggiorna periodicamente lo stato del gioco e lo trasmette ai client.
        """
        game = GameConsumer.games.get(self.game_id)
        if not game:
            return

        print(f"Starting game loop for game {self.game_id}")
        while game.clients:  # Esegui il ciclo finché ci sono client connessi
            if game.game_over:
                winner = self.game.left_player if game.state["left_score"] >= game.WINNING_SCORE else self.game.right_player
                loser = self.game.right_player if winner == self.game.left_player else self.game.left_player

                # Aggiorna i trofei
                await self.update_trophies(winner, loser)

                # Invia un messaggio di fine gioco ai client
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game.over",
                        "winner": winner.username,
                    }
                )
                break
            await game.update_game_state()
            await game.broadcast_state()
            await asyncio.sleep(1 / 60)  # Ciclo a 60 FPS

        # Una volta che non ci sono più giocatori connessi, ferma il loop
        game.game_loop_running = False

    async def send_json(self, content):
        """
        Funzione helper per inviare messaggi JSON al WebSocket.
        """
        await self.send(text_data=json.dumps(content))

    async def players_update(self, event):
        """
        Gestisce l'aggiornamento dei giocatori inviando un messaggio ai client.
        """
        await self.send_json({
            "type": "players_update",
            "left_player": event["left_player"],
            "left_player_trophies": event["left_player_trophies"],
            "right_player": event["right_player"],
            "right_player_trophies": event["right_player_trophies"],
        })
    
    async def game_over(self, event):
        """
        Gestisce la fine del gioco inviando un messaggio ai client.
        """
        await self.send_json({
            "type": "game_over",
            "winner": event["winner"],
        })

    @database_sync_to_async
    def update_trophies(self, winner, loser):
        """
        Aggiorna i trofei dei giocatori dopo la partita.
        """
        try:
            winner.trophies += 3  # Aggiungi trofei al vincitore
            loser.trophies = max(loser.trophies - 1, 0)  # Rimuovi trofei dal perdente (ma non scendere sotto zero)

            winner.save()
            loser.save()
        except Exception as e:
            print(f"Errore durante l'aggiornamento dei trofei: {e}")