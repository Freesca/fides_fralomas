<script setup>
import ProtectedRoute from '@/components/ProtectedRoute.vue';
import GameTab from '@/components/Game.vue';

</script>

<template>
	<ProtectedRoute>
		<GameTab />
	</ProtectedRoute>
</template>
