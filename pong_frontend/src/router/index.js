import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import RegisterView from '@/views/RegisterView.vue';
import LoginView from '@/views/LoginView.vue';
import { useAuthStore } from '@/stores/auth';
import LogoutView from '@/views/LogoutView.vue';
import GameView from '@/views/MatchmakingView.vue';
import GamePlayView from '@/views/GameView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/logout',
      name: 'logout',
      component: LogoutView
    },
    {
      path: '/game',
      name: 'game',
      component: GameView
    },

    {
      path: '/game/:game_id',
      name: 'game_play',
      component: GamePlayView
    }
  ],
});

// Global navigation guard to reset OTP state on page change
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (authStore.otpRequired) {
    // Reset the OTP state when switching between register and login
    authStore.otpRequired = false;
    authStore.userForOtp = null;
  }
  next();
});

export default router;
