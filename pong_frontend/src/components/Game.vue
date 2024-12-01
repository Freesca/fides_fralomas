<script>
import { useAuthStore } from '../stores/auth';
import { useRoute, useRouter } from 'vue-router';

export default {
	data() {
		return {
			connectionStatus: 'connecting',
			lastEvent: null,
			socket: null,
		};
	},
	created() {
		this.authStore = useAuthStore();
		this.router = useRouter();
		this.route = useRoute();
	},
	mounted() {
		if (!this.authStore.jwt.access) {
			console.error('No access token available');
			this.router.push('/');
			return;
		}

		const gameId = this.route.params?.game_id;
		if (!gameId) {
			this.$toast.error('No game id provided');
			this.router.push('/');
			return;
		}

		const socketUrl = `${import.meta.env.VITE_MATCH_WS_URL}/ws/game/${gameId}/`;
		this.socket = new WebSocket(socketUrl);

		// Handle WebSocket events
		this.socket.onopen = () => {
			this.connectionStatus = 'connected';
			console.log('Connected to the game server');

			const tokenPayload = JSON.stringify({ token: this.authStore.jwt.access });
			this.socket.send(this.authStore.jwt.access);
			console.log('Access token sent to server:', tokenPayload);
		};

		this.socket.onmessage = (event) => {
			console.log('Message from server:', event);

			const msg = JSON.parse(event.data);
			console.debug('Received message:', msg);

			this.lastEvent = event.data;
		};

		this.socket.onclose = () => {
			this.connectionStatus = 'disconnected';
			console.warn('Disconnected from game server');
			// this.router.push('/');
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
	beforeUnmount() {
		if (this.socket) {
			this.socket.close();
			console.log('Socket connection closed');
		}
	},
};
</script>

<template>
	<div>
		<p>Game ID: {{ $route.params.game_id }}</p>
		<p :class="{ 'text-danger': lastEvent?.type == 'error' }">Connection Status: {{ connectionStatus }}</p>
		<p v-if="connectionStatus == 'disconnected'">You will be redirected to the homepage in a few seconds.</p>
	</div>
</template>
