import axios from 'axios';
import { useAuthStore } from '../stores/auth';

export const axiosWrapper = axios.create({
	baseURL: 'http://localhost:9003', // Use your base URL here
});

axiosWrapper.interceptors.request.use(
	(config) => {
		const authStore = useAuthStore();
		if (authStore.jwt.access) {
			config.headers['Authorization'] = `Bearer ${authStore.jwt.access}`;
		}
		return config;
	},
	async (error) => {
		if (error.response && (error.response.status === 401 || error.response.status === 403 || error.response.status === 400)) {
			// Token expired or invalid, attempt to refresh the token
			const authStore = useAuthStore();
			try {
				await authStore.refreshAccessToken();
				// Retry the original request with the new access token
				error.config.headers['Authorization'] = `Bearer ${authStore.jwt.access}`;
				return axiosInstance.request(error.config);
			} catch (refreshError) {
				console.error('Token refresh failed:', refreshError);
				authStore.logout();
				return Promise.reject(refreshError);
			}
		}
		return Promise.reject(error);
	}
);