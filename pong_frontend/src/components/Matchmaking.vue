<script>
import router from '@/router';
import { axiosWrapper } from '@/utils/axiosWrapper';


export default {
	data() {
		return {
			isSearching: false,
			usedPassword: '',
		};
	},
	computed: {},
	methods: {
		async startLookup() {
			this.isSearching = true;
			const body = {
				password: this.usedPassword,
			};
			const req = await axiosWrapper.post(`${import.meta.env.VITE_MATCHMAKING_API_URL}/match/private-password/`, JSON.stringify(body), {
				timeout: 61 * 1000
			});
			console.log(req);
			if (req.status === 200) {
				console.log("FOUND", req.data);
				router.push(`/game/${req.data.game_id}`);
			} else {
				this.$toast.error(`Error: ${req.data.detail ?? ""}`);
			}
		}
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
			<RouterLink to="/">Cancel and go to homepage</RouterLink>
		</div>
	</div>
	<div v-else class="d-flex flex-column justify-content-center align-items-center">
		<h1>Search for a game</h1>
		<form @submit.prevent="startLookup" class="d-flex flex-column justify-content-center align-items-center">
			<div class="form-group">
				<input type="text" class="form-control" id="password" v-model="usedPassword" required placeholder="Enter the channel key">
			</div>
			<button type="submit" class="btn btn-outline-success mt-3">Start Lookup</button>
		</form>
		<div class="mt-5">
			<RouterLink to="/">Go back</RouterLink>
		</div>
	</div>
</template>