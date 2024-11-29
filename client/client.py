import json
import requests
import asyncio
import websockets
import json
import pygame
import sys

BASE_URL = "http://localhost:8000"  # Modifica con l'URL del tuo microservizio
MATCH_URL = "http://localhost:8001"  # Modifica con l'URL del tuo microservizio

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100


def register_user():
    """Registra un utente."""
    print("Registrazione utente")
    email = input("Inserisci l'email: ")
    username = input("Inserisci lo username: ")
    password = input("Inserisci la password: ")
    password_confirm = input("Conferma la password: ")

    url = f"{BASE_URL}/register/"
    data = {
        "email": email,
        "username": username,
        "password": password,
        "password_confirm": password_confirm
    }

    response = requests.post(url, json=data)
    print("Risposta alla registrazione:", response.json())
    return response.status_code == 201  # Restituisce True se la registrazione è stata completata


def login_user():
    """Effettua il login e restituisce i token."""
    print("Login utente")
    username = input("Inserisci l'username: ")
    password = input("Inserisci la password: ")

    url = f"{BASE_URL}/login/"
    data = {
        "username": username,
        "password": password
    }

    response = requests.post(url, json=data)
    print("Risposta al login:", response.json())
    return response.status_code == 200  # Restituisce True se il login è riuscito


def verify_otp():
    """Verifica il codice OTP e salva i token."""
    print("Verifica del codice OTP")
    email = input("Inserisci l'email per la verifica OTP: ")
    otp_code = input("Inserisci il codice OTP: ")

    url = f"{BASE_URL}/verify-otp/"
    data = {
        "email": email,
        "otp_code": otp_code
    }

    response = requests.post(url, json=data)
    tokens = response.json()
    if response.status_code == 200:
        print("Verifica OTP riuscita:", tokens)
        return tokens  # Restituisce i token se la verifica è riuscita
    else:
        print("Errore nella verifica OTP:", response.json())
        return None


def get_with_auth(endpoint, token):
    """Effettua una richiesta GET con autorizzazione Bearer."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response


def refresh_access_token(refresh_token):
    """Richiede un nuovo access token utilizzando il refresh token."""
    url = f"{BASE_URL}/token_refresh/"
    data = {"refresh": refresh_token}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        new_access_token = response.json().get("access")
        print("Nuovo access token ricevuto:", new_access_token)
        return new_access_token
    else:
        print("Errore nel refresh del token:", response.json())
        return None


def send_matchmaking_request(password, token):
    """Invia una richiesta di matchmaking con una password."""
    url = f"{MATCH_URL}/match/private-password/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {"password": password}
    response = requests.post(url, json=data, headers=headers, timeout=65)
    if response.status_code == 200:
        print("Risposta matchmaking:", response.json())
    else:
        print("Errore matchmaking:", response.status_code, response.json())
        return None
    game_id = response.json().get("game_id")
    try:
        asyncio.run(game_client(game_id, token))
    except KeyboardInterrupt:
        print("Interruzione manuale del programma.")
    except Exception as e:
        print(f"Errore nel client: {e}")
    finally:
        pygame.quit()
        sys.exit()

async def game_client(game_id, token):
    """
    Client per la connessione al server Pong.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong")

    async with websockets.connect(f"ws://localhost:8002/ws/game/{game_id}/") as websocket:
        # Loop principale
        clock = pygame.time.Clock()

        #invia il token di autorizzazione  
        await websocket.send(token)

        # Determina il lato del giocatore
        response = await websocket.recv()
        print("Risposta dal server1:", response)
        player_side = json.loads(response).get("player_side")
        while True:
            # Cattura input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                break

            # Invia input al server
            if player_side == "left":
                if keys[pygame.K_w]:
                    print(f"{player_side} w")
                    await websocket.send(json.dumps({"action": "move", "direction": "up"}))
                if keys[pygame.K_s]:
                    print(f"{player_side} s")
                    await websocket.send(json.dumps({"action": "move", "direction": "down"}))
            elif player_side == "right":
                if keys[pygame.K_UP]:
                    print(f"{player_side} up")
                    await websocket.send(json.dumps({"action": "move", "direction": "up"}))
                if keys[pygame.K_DOWN]:
                    print(f"{player_side} down")
                    await websocket.send(json.dumps({"action": "move", "direction": "down"}))

            # Ricevi lo stato aggiornato dal server
            response = await websocket.recv()
            state = json.loads(response)

            # Disegna lo stato aggiornato
            screen.fill(BLACK)
            pygame.draw.rect(screen, WHITE, (10, state["left_paddle"]["y"], PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.rect(
                screen,
                WHITE,
                (SCREEN_WIDTH - PADDLE_WIDTH - 10, state["right_paddle"]["y"], PADDLE_WIDTH, PADDLE_HEIGHT),
            )
            pygame.draw.ellipse(
                screen, WHITE, (state["ball"]["x"], state["ball"]["y"], BALL_SIZE, BALL_SIZE)
            )
            font = pygame.font.Font(None, 74)
            text = font.render(
                f"{state['left_score']} - {state['right_score']}", True, WHITE
            )
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))
            pygame.display.flip()
            clock.tick(60)

def patch_with_auth(endpoint, token, data):
    """Effettua una richiesta PATCH con autorizzazione Bearer."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.patch(url, json=data, headers=headers)
    return response


def main():
    print("Benvenuto! Scegli un'opzione:")
    choice = input("Vuoi registrarti o fare il login? (register/login): ").strip().lower()

    if choice == "register":
        # Registrazione utente
        if not register_user():
            print("Registrazione fallita. Interrompo il processo.")
            return

        # Verifica OTP e recupero dei token
        tokens = verify_otp()
        if tokens is None:
            print("Verifica OTP fallita. Interrompo il processo.")
            return

    elif choice == "login":
        # Login utente
        if not login_user():
            print("Login fallito. Interrompo il processo.")
            return
        tokens = verify_otp()
        if tokens is None:
            print("Verifica OTP fallita. Interrompo il processo.")
            return
    else:
        print("Scelta non valida. Riprova.")
        return

    # Recupera i token
    access_token = tokens.get("access")
    refresh_token = tokens.get("refresh")

    # Comando per varie azioni
    while True:
        command = input("Inserisci il comando (profile, user/<username>, list, refresh, match, exit per uscire): ").strip()
        if command == "exit":
            command = input("Vuoi uscire con logout? (yes/no): ").strip()
            if command == "yes":
                response = requests.post(f"{BASE_URL}/logout/", headers={"Authorization": f"Bearer {access_token}"})
                print("Risposta:", response.status_code)
            print("Uscita dal client.")
            break

        if command == "profile":
            action = input("Vuoi visualizzare o modificare il profilo? (get/patch): ").strip().lower()
            if action == "get":
                # Effettua una richiesta GET
                endpoint = "profile/"
                response = get_with_auth(endpoint, access_token)
                if response.status_code == 200:
                    print("Risposta:", json.dumps(response.json(), indent=4))
                else:
                    print("Errore:", response.status_code, response.json())
            elif action == "patch":
                # Effettua una richiesta PATCH
                field = input("Quale campo vuoi modificare? (email/username/password): ").strip().lower()
                data = {}
                if field == "email":
                    new_email = input("Inserisci la nuova email: ").strip()
                    data = {"email": new_email}
                elif field == "username":
                    new_username = input("Inserisci il nuovo username: ").strip()
                    data = {"username": new_username}
                elif field == "password":
                    current_password = input("Inserisci la password attuale: ").strip()
                    new_password = input("Inserisci la nuova password: ").strip()
                    confirm_new_password = input("Conferma la nuova password: ").strip()
                    data = {
                        "current_password": current_password,
                        "new_password": new_password,
                        "confirm_new_password": confirm_new_password,
                    }
                else:
                    print("Campo non valido. Riprova.")
                    continue

                response = patch_with_auth("profile/", access_token, data)
                if response.status_code == 200:
                    print("Modifica riuscita:", response.json())
                else:
                    print("Errore nella modifica:", response.status_code, response.json())
            else:
                print("Azione non valida. Riprova.")

        elif command.startswith("user/"):
            endpoint = command + "/"
            response = get_with_auth(endpoint, access_token)
            if response.status_code == 200:
                print("Risposta:", json.dumps(response.json(), indent=4))
            else:
                print("Errore:", response.status_code, response.json())

        elif command == "list":
            endpoint = "user_list/"
            response = get_with_auth(endpoint, access_token)
            if response.status_code == 200:
                print("Risposta:", json.dumps(response.json(), indent=4))
            else:
                print("Errore:", response.status_code, response.json())

        elif command == "refresh":
            # Richiede un nuovo access token
            new_access_token = refresh_access_token(refresh_token)
            if new_access_token:
                access_token = new_access_token

        elif command == "match":
            # Invia una richiesta di matchmaking
            password = input("Inserisci la password per il matchmaking: ")
            send_matchmaking_request(password, access_token)

        else:
            print("Comando non valido. Riprova.")

if __name__ == "__main__":
    main()
