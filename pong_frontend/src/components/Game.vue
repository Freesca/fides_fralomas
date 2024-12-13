<script>
import { useAuthStore } from '../stores/auth';
import { useRoute, useRouter } from 'vue-router';

/** @typedef {{ x: number, y: number }} Position */
/** @typedef {{ y: number }} Paddle */
/** @typedef {{ ball: Position, left_paddle: Paddle, right_paddle: Paddle, left_score: number, right_score: number }} GameState */

export default {
	data() {
		return {
			REFERENCE_WIDTH: 800,
			REFERENCE_HEIGHT: 600,
			canvasWidth: 600, // Reduce canvas size to make the game area smaller
			canvasHeight: 450, // Reduce canvas size to make the game area smaller

			connectionStatus: 'connecting',
			lastEvent: null,
			socket: null,
			playerSide: null,
			gameState: null,
			canvas: null,
			ctx: null,
			leftPlayer: null,
			rightPlayer: null,
			leftPlayerTrophies: null,
			rightPlayerTrophies: null,
			gameOver: false,
			winner: null,
		};
	},
	created() {
		this.authStore = useAuthStore();
		this.router = useRouter();
		this.route = useRoute();
	},
	mounted() {
		const gameId = this.route.params?.game_id;
		if (!gameId) {
			this.$toast.error('No game id provided');
			this.router.push('/');
			return;
		}

		this.setupSocket(gameId);
		this.setupCanvas();
		this.resizeCanvas();

		window.addEventListener('resize', this.resizeCanvas);
		window.addEventListener('keydown', this.handleKeyPress);
	},
	beforeUnmount() {
		if (this.socket) {
			this.socket.close();
			console.debug('Socket connection closed');
		}
		window.removeEventListener('keydown', this.handleKeyPress);
		window.removeEventListener('resize', this.resizeCanvas);
	},
	methods: {
		setupCanvas() {
			this.canvas = this.$refs.gameCanvas;
			this.ctx = this.canvas.getContext('2d');
		},
		resizeCanvas() {
			const scale = Math.min(
				window.innerWidth / this.REFERENCE_WIDTH,
				window.innerHeight / this.REFERENCE_HEIGHT
			);
			this.canvasWidth = this.REFERENCE_WIDTH * scale * 0.75; // Scale down the game area
			this.canvasHeight = this.REFERENCE_HEIGHT * scale * 0.75; // Scale down the game area

			this.canvas.width = this.canvasWidth;
			this.canvas.height = this.canvasHeight;

			if (this.gameState) {
				this.renderGame();
			}
		},
		/** @param {KeyboardEvent} event */
		handleKeyPress(event) {
			if (!this.socket || !this.playerSide) return;

			let direction = null;
			if (event.key === 'ArrowUp' || event.key === 'w') {
				direction = 'up';
			} else if (event.key === 'ArrowDown' || event.key === 's') {
				direction = 'down';
			}

			if (direction) {
				const moveMessage = JSON.stringify({ action: 'move', direction });
				this.socket.send(moveMessage);
				console.log(`Sent move: ${direction}`);
			}
		},
		renderGame() {
			if (!this.ctx || !this.gameState) return;

			const { ball, left_paddle, right_paddle, left_score, right_score } = this.gameState;

			const scaleX = this.canvasWidth / this.REFERENCE_WIDTH;
			const scaleY = this.canvasHeight / this.REFERENCE_HEIGHT;

			// Clear
			this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

			// Draw border around the game area
			this.ctx.strokeStyle = 'white';
			this.ctx.lineWidth = 4;
			this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);

			// Draw dashed center line
			if (!this.gameOver) {
				this.ctx.setLineDash([10 * scaleX, 15 * scaleX]);
				this.ctx.beginPath();
				this.ctx.moveTo(this.canvas.width / 2, 0);
				this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
				this.ctx.strokeStyle = 'white';
				this.ctx.lineWidth = 4;
				this.ctx.stroke();
				this.ctx.setLineDash([]);
			}
			// Ball
			if (!this.gameOver) {
			this.ctx.fillStyle = 'white';
			this.ctx.beginPath();
			this.ctx.arc(ball.x * scaleX, ball.y * scaleY, 10 * scaleX, 0, Math.PI * 2);
			this.ctx.fill();
			}

			// Paddles
			this.ctx.fillRect(0, left_paddle.y * scaleY, 20 * scaleX, 100 * scaleY); // Left paddle
			this.ctx.fillRect(this.canvas.width - 20 * scaleX, right_paddle.y * scaleY, 20 * scaleX, 100 * scaleY); // Right paddle

			// Draw the scores
			this.ctx.font = `bold ${30 * scaleX}px "Press Start 2P"`; // Pixelated font
			this.ctx.fillStyle = 'white';
			this.ctx.textAlign = 'center';
			this.ctx.fillText(left_score, (this.canvas.width / 4), 80 * scaleY);
			this.ctx.fillText(right_score, (this.canvas.width * 3) / 4, 80 * scaleY);

			// Draw player names and trophies above the score, outside the game board
			if (this.leftPlayer && this.rightPlayer) {
				this.ctx.font = `bold ${15 * scaleX}px "Press Start 2P"`; // Pixelated font for names
				this.ctx.fillText(`${this.leftPlayer} (Trophies: ${this.leftPlayerTrophies})`, (this.canvas.width / 4), 30 * scaleY);
				this.ctx.fillText(`${this.rightPlayer} (Trophies: ${this.rightPlayerTrophies})`, (this.canvas.width * 3) / 4, 30 * scaleY);
			}

			// Draw game over message if game is over
			if (this.gameOver) {
				this.ctx.font = `bold ${20 * scaleX}px "Press Start 2P"`;
				this.ctx.fillStyle = 'white';
				this.ctx.textAlign = 'center';
				this.ctx.fillText(`Game Over!`, this.canvas.width / 2, this.canvas.height / 2 - 30 * scaleY);
				this.ctx.fillText(`Winner: ${this.winner}`, this.canvas.width / 2, this.canvas.height / 2); 
			}
		},
		setupSocket(gameId) {
			const socketUrl = `${import.meta.env.VITE_MATCH_WS_URL}/ws/game/${gameId}/`;
			this.socket = new WebSocket(socketUrl);

			this.socket.onopen = () => {
				this.connectionStatus = 'connected';
				const tokenPayload = this.authStore.jwt.access;
				this.socket.send(tokenPayload);
				console.debug('Access token sent to server:', tokenPayload);
			};

			this.socket.onmessage = (event) => {
				const msg = JSON.parse(event.data);
				console.log(event)
				console.debug('Received message:', msg);

				if (msg.type === "game_over") {
					this.gameOver = true;
					this.winner = msg.winner;
					this.renderGame();
				} else if (!this.playerSide && msg.player_side) {
					// First message received from server: contains the player side
					this.playerSide = msg.player_side;
					console.debug(`Player side: ${this.playerSide}`);
				} else if (msg.ball) {
					// Game state update
					this.gameState = msg;
					this.renderGame();
				} else if (msg.type === 'players_update') {
					// Player update message
					this.leftPlayer = msg.left_player;
					this.leftPlayerTrophies = msg.left_player_trophies;
					this.rightPlayer = msg.right_player;
					this.rightPlayerTrophies = msg.right_player_trophies;
					this.renderGame();
				}

				this.lastEvent = event.data;
			};

			this.socket.onclose = () => {
				this.connectionStatus = 'disconnected';
				console.warn('Disconnected from game server');
				setTimeout(() => {
					this.router.push('/');
				}, 5000);
			};

			this.socket.onerror = (error) => {
				console.error('Socket error:', error);
				this.connectionStatus = 'disconnected';
				this.lastEvent = error;
				setTimeout(() => {
					this.router.push('/');
				}, 5000);
			};
		},
	},
};
</script>

<template>
	<div>
		<p>Game ID: {{ $route.params.game_id }}</p>
		<p :class="{ 'text-danger': lastEvent?.type == 'error' }">Connection Status: {{ connectionStatus }}</p>
		<p v-if="connectionStatus == 'disconnected'">You will be redirected to the homepage in a few seconds.</p>
		<canvas ref="gameCanvas" :width="canvasWidth" :height="canvasHeight" style="background: black;"></canvas>
	</div>
	<div>
		<RouterLink class="btn btn-outline-danger" to="/">Get out of here</RouterLink>
	</div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

canvas {
	border: 1px solid white;
	margin-top: 20px;
	width: 75%;
	height: auto;
	max-width: 800px;
	max-height: 600px;
}
</style>
