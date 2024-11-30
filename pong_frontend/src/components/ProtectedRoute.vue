<template>
	<div v-if="isAuthenticated">
		<slot></slot>
	</div>
	<div v-else>
		<p>Loading...</p>
	</div>
</template>

<script>
import { useAuthStore } from '../stores/auth';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
	setup() {
		const authStore = useAuthStore();
		const router = useRouter();
		const isAuthenticated = ref(false);
		const isLoading = ref(true);

		onMounted(async () => {
			if (authStore.jwt.access && !authStore.isAccessTokenExpired()) {
				// Token is valid and not expired
				isAuthenticated.value = true;
				isLoading.value = false;
			} else if (authStore.jwt.refresh) {
				try {
					// Attempt to refresh the access token
					await authStore.refreshAccessToken();
					isAuthenticated.value = true;
				} catch (error) {
					// Refresh token failed, redirect to login
					isAuthenticated.value = false;
					router.push('/login');
				} finally {
					isLoading.value = false;
				}
			} else {
				// No valid tokens available
				isAuthenticated.value = false;
				isLoading.value = false;
				router.push('/login');
			}
			if (isAuthenticated.value) {
				// Get user info
				authStore.getUserInfo();
			}
		});

		return {
			isAuthenticated,
			isLoading,
		};
	},
};
</script>
