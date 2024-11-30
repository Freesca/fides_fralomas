import './assets/main.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';
import { useAuthStore } from './stores/auth';
import {Toaster} from '@meforma/vue-toaster'


const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(Toaster)

const authStore = useAuthStore();
authStore.loadJwtFromStorage();


app.mount('#app');
