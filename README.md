# fides_fralomas
Pong Multiplayer Project

This repository contains a Django-based backend and a frontend for a multiplayer Pong game. The project is containerized using Docker for easy setup and deployment.
Getting Started
Prerequisites

  Docker and Docker Compose installed on your machine.
  Optional: Node.js installed for manual frontend setup.

Quick Start with Docker

  Clone the repository:

    git clone <repository_url>
    cd <repository_directory>

Start the services:

    make

Access the frontend: Open
        
        http://localhost:3000/
in your browser.

Login/Registration and OTP Verification:

After logging in or registering, you will be prompted for an OTP code.
To retrieve the OTP, use the following command:

        make get-last-sent-email

Manual Setup (If Docker Fails)
Steps:

  Prepare .env Files:
      Create a .env file in the root directory of each microservice (matchmaking_microservice/, pong_game_microservice/, user_menagement_microservice/).
      Add the following content:

    SIGNING_KEY=example_key

Run the initialization script:

    ./init-python.sh

For each microservice:

  Navigate into the microservice directory:

    cd <microservice_directory>

Start the server:

    ./start.sh

For the frontend:

  Navigate to the frontend directory:

    cd pong_frontend

Install dependencies:

    npm install

Start the development server:

        npm run dev

  Open
    
    http://localhost:3000/
  in your browser.

How to Play

  Open two separate browser sessions (or incognito windows).
  Log in with two different accounts.
  Enter the same game password in both sessions.
  The game will start automatically, connecting the two players.

Development Tools
Makefile Commands

    make 
  Start all services using Docker Compose.
  
    make get-last-sent-email 
  Retrieve the most recent OTP sent to the "user email" folder.

Directories

  matchmaking_microservice/ – Handles game matchmaking.
  pong_game_microservice/ – Manages the real-time game logic using WebSockets.
  user_management_microservice/ – Handles user authentication and management.
  pong_frontend/ – Frontend built with Node.js.

Known Issues

  Ensure Docker is properly installed and running before using make.
  If services fail to start, create .env files for each microservice as described in the Manual Setup section and use the manual steps.
