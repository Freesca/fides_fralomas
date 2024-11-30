import { defineStore } from 'pinia';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import { axiosWrapper } from '@/utils/axiosWrapper';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
	state: () => ({
		user: null,
		jwt: {
			access: null,
			refresh: null,
		},
		errors: {},
		isLoading: false,
		otpRequired: false,
		userForOtp: null,
	}),
	actions: {
		/**
		 * Load JWT from localStorage if available
		 */
		loadJwtFromStorage() {
			const access = localStorage.getItem('access_token');
			const refresh = localStorage.getItem('refresh_token');
			if (access && refresh) {
				this.jwt = { access, refresh };
			}
		},
		/**
		 * Save JWT to localStorage
		 * @param {Object} tokens - The JWT tokens to store
		 */
		saveJwtToStorage(tokens) {
			localStorage.setItem('access_token', tokens.access);
			localStorage.setItem('refresh_token', tokens.refresh);
		},
		/**
		 * Clear JWT from localStorage
		 */
		clearJwtFromStorage() {
			localStorage.removeItem('access_token');
			localStorage.removeItem('refresh_token');
		},
		/**
		 * @param {{email: string, username: string, password: string, passwordConfirm: string}} formData
		 */
		async register(formData) {
			this.isLoading = true;
			this.errors = {};
			try {
				const response = await axios.post(`${import.meta.env.VITE_USER_API_URL}/register/`, formData);
				this.otpRequired = true;
				this.userForOtp = formData.username;
			} catch (error) {
				if (error.response && error.response.data) {
					this.errors = error.response.data;
				} else {
					console.error('Registration failed:', error);
				}
			} finally {
				this.isLoading = false;
			}
		},
		async confirmOtp(otpCode) {
			this.isLoading = true;
			this.errors = {};
			let success = false;
			try {
				const response = await axios.post(`${import.meta.env.VITE_USER_API_URL}/verify-otp/`, {
					username: this.userForOtp,
					otp_code: otpCode,
				});
				const tokens = {
					access: response.data.access,
					refresh: response.data.refresh,
				};
				this.jwt = tokens;
				this.user = response.data.user;
				this.otpRequired = false; // OTP step completed
				this.userForOtp = null;
				this.saveJwtToStorage(tokens);
				success = true;
			} catch (error) {
				if (error.response && error.response.data) {
					this.errors = error.response.data;
				} else {
					console.error('OTP confirmation failed:', error);
				}

			} finally {
				this.isLoading = false;
				return success;
			}
		},
		/**
		 * @param {{email: string, username: string, password: string, passwordConfirm: string}} formData
		 */
		async login(formData) {
			this.isLoading = true;
			this.errors = {};
			try {
				const response = await axios.post(`${import.meta.env.VITE_USER_API_URL}/login/`, formData);
				const tokens = {
					access: response.data.access,
					refresh: response.data.refresh,
				};
				this.jwt = tokens;
				this.user = response.data.user;
				this.otpRequired = false;
				this.userForOtp = null;
				this.saveJwtToStorage(tokens); // Save tokens to localStorage
			} catch (error) {
				if (error.response && error.response.status === 401) {
					// OTP required
					this.otpRequired = true;
					this.userForOtp = formData.username;
				} else if (error.response && error.response.data) {
					this.errors = error.response.data;
				} else {
					console.error('Login failed:', error);
				}
			} finally {
				this.isLoading = false;
			}
		},
		logout() {
			this.user = null;
			this.jwt = {
				access: null,
				refresh: null,
			};
			this.otpRequired = false;
			this.userForOtp = null;
			this.clearJwtFromStorage();
			router.push('/login');
		},

		// JWT-related methods
		isAccessTokenExpired() {
			if (!this.jwt.access) return true; // No token means expired
			try {
				const decoded = jwtDecode(this.jwt.access);
				return decoded.exp * 1000 < Date.now();
			} catch (error) {
				console.error('Failed to decode JWT:', error);
				return true; // Treat as expired if decoding fails
			}
		},

		async refreshAccessToken() {
			this.isLoading = true;
			try {
				const response = await axios.post(`${import.meta.env.VITE_USER_API_URL}/token_refresh/`, {
					refresh: this.jwt.refresh,
				});
				const tokens = {
					access: response.data.access,
					refresh: this.jwt.refresh, // Keep the refresh token unchanged
				};
				this.jwt = tokens;
				this.saveJwtToStorage(tokens); // Save updated tokens to localStorage
			} catch (error) {
				console.error('Token refresh failed:', error);
				this.clearJwtFromStorage();
				throw error;
			} finally {
				this.isLoading = false;
			}
		},

		// Get user info
		async getUserInfo() {
			this.isLoading = true;
			try {
				const response = await axiosWrapper.get(`${import.meta.env.VITE_USER_API_URL}/profile/`);
				this.user = response.data;
			} catch (error) {
				console.error('User info retrieval failed:', error);
			} finally {
				this.isLoading = false;
			}
		},

	},
});
