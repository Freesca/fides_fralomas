import asyncio
import json

class PongGame:
    def __init__(self, game_id):
        self.game_id = game_id
        self.state = {
            "ball": {"x": 400, "y": 300, "dx": 6, "dy": 0},
            "left_paddle": {"y": 250},
            "right_paddle": {"y": 250},
            "left_score": 0,
            "right_score": 0,
        }
        self.clients = []

    async def process_input(self, client, input_data):
        """
        Process input from a player.
        """

        print(f"Processing input from {client}: {input_data}")
        paddle_speed = 5
        if input_data.get("action") == "move":
            direction = input_data.get("direction")
            if client == "left" and direction == "up" and self.state["left_paddle"]["y"] > 0:
                self.state["left_paddle"]["y"] -= paddle_speed
            elif client == "left" and direction == "down" and self.state["left_paddle"]["y"] < 500:
                self.state["left_paddle"]["y"] += paddle_speed
            elif client == "right" and direction == "up" and self.state["right_paddle"]["y"] > 0:
                self.state["right_paddle"]["y"] -= paddle_speed
            elif client == "right" and direction == "down" and self.state["right_paddle"]["y"] < 500:
                self.state["right_paddle"]["y"] += paddle_speed

    async def update_game_state(self):
        """
        Update game logic: ball position, collisions, scores.
        """
        ball = self.state["ball"]

        # Update ball position
        ball["x"] += ball["dx"]
        ball["y"] += ball["dy"]

        # Collision with top and bottom walls
        if ball["y"] <= 0 or ball["y"] >= 580:
            ball["dy"] = -ball["dy"]

        # Collision with paddles
        if (
            ball["x"] <= 20
            and self.state["left_paddle"]["y"] <= ball["y"] <= self.state["left_paddle"]["y"] + 100
        ):
            ball["dx"] = -ball["dx"]
            offset = (ball["y"] - self.state["left_paddle"]["y"]) - 50
            ball["dy"] = offset // 10

        if (
            ball["x"] >= 760
            and self.state["right_paddle"]["y"] <= ball["y"] <= self.state["right_paddle"]["y"] + 100
        ):
            ball["dx"] = -ball["dx"]
            offset = (ball["y"] - self.state["right_paddle"]["y"]) - 50
            ball["dy"] = offset // 10

        # Handle scoring
        if ball["x"] < 0:
            self.state["right_score"] += 1
            self.reset_ball()
        elif ball["x"] > 800:
            self.state["left_score"] += 1
            self.reset_ball()

    def reset_ball(self):
        """
        Reset the ball's position to the center.
        """
        self.state["ball"] = {"x": 400, "y": 300, "dx": 6, "dy": 0}

    async def broadcast_state(self):
        """
        Broadcast the updated game state to all connected clients.
        """
        for client in self.clients:
            await client.send_json(self.state)
