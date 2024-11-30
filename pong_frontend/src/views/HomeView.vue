<script setup>
import ProtectedRoute from '@/components/ProtectedRoute.vue';
import StartingLayout from '@/components/StartingLayout.vue';
import { useAuthStore } from '@/stores/auth';
import { RouterLink } from 'vue-router';
const authStore = useAuthStore();
</script>

<template>
  <StartingLayout />
  <ProtectedRoute>

    <main>
      <h1>Pong Game</h1>
      <p>Welcome to the Pong Game, <b>{{ authStore.user?.username }}</b>!</p>
      <p>This is a simple game where you try to get the ball to the other side of the screen.</p>
      <p>The goal is to score 10 points against your opponent.</p>
      <p>Good luck!</p>

      <RouterLink class="btn btn-lg btn-outline-success" to="/game">Play</RouterLink>
    </main>
  </ProtectedRoute>
</template>
