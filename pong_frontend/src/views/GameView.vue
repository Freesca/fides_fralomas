<script setup>
import ProtectedRoute from '@/components/ProtectedRoute.vue';
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>

<template>
	<ProtectedRoute>

		<main>
			<h2>WIP...</h2>
		</main>
		<RouterLink to="/">Back to home</RouterLink>
	</ProtectedRoute>
</template>
