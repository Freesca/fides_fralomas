import requests
import json

BASE_URL = "http://localhost:8000"  # Modifica con l'URL del tuo microservizio
MATCH_URL = "http://localhost:8001"  # Modifica con l'URL del tuo microservizio


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
            endpoint = "profile/"
        elif command.startswith("user/"):
            endpoint = command + "/"
        elif command == "list":
            endpoint = "user_list/"
        elif command == "refresh":
            # Richiede un nuovo access token
            new_access_token = refresh_access_token(refresh_token)
            if new_access_token:
                access_token = new_access_token
            continue
        elif command == "match":
            # Invia una richiesta di matchmaking
            password = input("Inserisci la password per il matchmaking: ")
            send_matchmaking_request(password, access_token)
            continue
        else:
            print("Comando non valido. Riprova.")
            continue

        # Effettua la richiesta GET al server
        response = get_with_auth(endpoint, access_token)
        if response.status_code == 200:
            print("Risposta:", json.dumps(response.json(), indent=4))
        else:
            print("Errore:", response.status_code, response.json())


if __name__ == "__main__":
    main()

