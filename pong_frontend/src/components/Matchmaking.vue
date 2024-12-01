<script>
import router from '@/router';
import { axiosWrapper } from '@/utils/axiosWrapper';

export default {
	data() {
		return {
			isSearching: false,
			usedPassword: '',
			abortController: null,
		};
	},
	methods: {
		cancel() {
			if (this.abortController) {
				this.abortController.abort();
				console.log('Search request canceled by user.');
				this.isSearching = false;
			}
		},
		async startLookup() {
			this.isSearching = true;

			this.abortController = new AbortController();

			const body = {
				password: this.usedPassword,
			};

			try {
				const req = await axiosWrapper.post(
					`${import.meta.env.VITE_MATCHMAKING_API_URL}/match/private-password/`,
					JSON.stringify(body),
					{
						timeout: 61 * 1000,
						signal: this.abortController.signal,
					}
				);

				if (req.status === 200) {
					console.log('FOUND', req.data);
					const data = req.data.game_id;
					const gameId = data.game_id ?? data;
					router.push(`/game/${gameId}/`);
				} else {
					this.$toast.error(`Error: ${req.data.detail ?? ''}`);
				}
			} catch (error) {
				if (error.name === 'AbortError' || error.name === 'CanceledError') {
					console.info('Matchmaking request canceled by user.', error);
				} else {
					console.error('Error: ', error);
					this.$toast.error(`Error: ${error.response?.data?.detail ?? 'Unexpected error'}`);
				}
			} finally {
				this.isSearching = false;
				this.abortController = null;
			}
		},
	},
};
</script>

<template>
	<div v-if="isSearching" class="d-flex flex-column justify-content-center align-items-center">
		<div class="d-flex flex-column justify-content-center align-items-center">
			<h1>Searching for a game...</h1>
			<i class="fa-solid fa-spinner fa-spin"></i>
		</div>
		<div>
			<small>Code: {{ usedPassword }}</small>
		</div>
		<div class="mt-5">
			<button class="btn btn-outline-warning" @click="cancel">Cancel</button>
		</div>
	</div>
	<div v-else class="d-flex flex-column justify-content-center align-items-center">
		<h1>Search for a game</h1>
		<form @submit.prevent="startLookup" class="d-flex flex-column justify-content-center align-items-center">
			<div class="form-group">
				<input
					type="text"
					class="form-control"
					id="password"
					v-model="usedPassword"
					required
					placeholder="Enter the channel key"
				/>
			</div>
			<button type="submit" class="btn btn-outline-success mt-3">Start Lookup</button>
		</form>
		<div class="mt-5">
			<RouterLink to="/">Go back</RouterLink>
		</div>
	</div>
</template>
