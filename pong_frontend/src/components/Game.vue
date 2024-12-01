<script>
import { useAuthStore } from '../stores/auth';
import { useRoute, useRouter } from 'vue-router';

/** @typedef {{ x: number, y: number }} Position */
/** @typedef {{ y: number }} Paddle */
/** @typedef {{ ball: Position, left_paddle: Paddle, right_paddle: Paddle, left_score: number, right_score: number }} GameState */

export default {
	data() {
		return {
			GAME_WIDTH: 800,
			GAME_HEIGHT: 560,

			connectionStatus: 'connecting',
			lastEvent: null,
			socket: null,
			playerSide: null,
			/** @type {GameState | null} */
			gameState: null,
			/** @type {HTMLCanvasElement} */
			canvas: null,
			/** @type {CanvasRenderingContext2D} */
			ctx: null,
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
		window.addEventListener('keydown', this.handleKeyPress);
	},
	beforeUnmount() {
		if (this.socket) {
			this.socket.close();
			console.debug('Socket connection closed');
		}
		window.removeEventListener('keydown', this.handleKeyPress);
	},
	methods: {
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
				console.debug('Received message:', msg);

				if (!this.playerSide && msg.player_side) {
					// First message received from server: contains the player side
					this.playerSide = msg.player_side;
					console.debug(`Player side: ${this.playerSide}`);
				} else if (msg.ball) {
					// Game state update
					this.gameState = msg;
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
		setupCanvas() {
			this.canvas = this.$refs.gameCanvas;
			this.ctx = this.canvas.getContext('2d');
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

			// Clear
			this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

			// Ball
			this.ctx.fillStyle = 'white';
			this.ctx.beginPath();
			this.ctx.arc(ball.x, ball.y, 5, 0, Math.PI * 2);
			this.ctx.fill();

			// Paddles
			this.ctx.fillRect(20, left_paddle.y, 10, 50); // Left paddle
			this.ctx.fillRect(this.canvas.width - 30, right_paddle.y, 10, 50); // Right paddle

			// Draw the scores
			this.ctx.font = '20px Arial';
			this.ctx.fillText(left_score, this.canvas.width / 4, 20);
			this.ctx.fillText(right_score, (this.canvas.width * 3) / 4, 20);
		},
	},
};
</script>

<template>
	<div>
		<p>Game ID: {{ $route.params.game_id }}</p>
		<p :class="{ 'text-danger': lastEvent?.type == 'error' }">Connection Status: {{ connectionStatus }}</p>
		<p v-if="connectionStatus == 'disconnected'">You will be redirected to the homepage in a few seconds.</p>
		<canvas ref="gameCanvas" :width="GAME_WIDTH" :height="GAME_HEIGHT" style="background: black;"></canvas>
	</div>
	<div>
		<RouterLink class="btn btn-outline-danger" to="/">Get out of here</RouterLink>
	</div>
</template>
