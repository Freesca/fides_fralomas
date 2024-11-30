<script setup>
import { useAuthStore } from '@/stores/auth';
import { onMounted } from 'vue';
const authStore = useAuthStore();
onMounted(() => {
  authStore.logout();
});
</script>

<template>

</template>
