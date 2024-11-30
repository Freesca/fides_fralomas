<script setup>
import ProtectedRoute from '@/components/ProtectedRoute.vue';
import Matchmaking from '@/components/Matchmaking.vue';

</script>

<template>
	<ProtectedRoute>
		<Matchmaking />
	</ProtectedRoute>
</template>
