<template>
	<div class="login">
		<h2>Login</h2>
		<form @submit.prevent="handleLogin">
			<div class="form-group">
				<label class="form-label" for="username">username</label>
				<input class="form-control" type="username" v-model="form.username" id="username" required autocomplete="username" />
				<span class="form-text form-error" v-if="errors.username" v-html="errors.username.join('<br>')"></span>
			</div>
			<div class="form-group">
				<label class="form-label" for="password">Password</label>
				<input class="form-control" type="password" v-model="form.password" id="password" required autocomplete="current-password" />
				<span class="form-text form-error" v-if="errors.password" v-html="errors.password.join('<br>')"></span>
			</div>
			<button v-if="!otpRequired" class="btn btn-success" type="submit" :disabled="isLoading">Login</button>
		</form>

		<div v-if="otpRequired" class="mt-2">
			<form @submit.prevent="handleOtpConfirmation">
				<div class="form-group">
					<label class="form-label" for="otp">
						<h6>OTP</h6>
					</label>
					<input class="form-control" type="text" v-model="otpCode" id="otp" required placeholder="Enter OTP" />
					<span class="form-text text-info">(sent to your email address)</span>
				</div>
				<button class="btn btn-success" type="submit" :disabled="isLoading">Confirm OTP</button>
			</form>
		</div>
	</div>
</template>

<script>
import router from '@/router';
import { useAuthStore } from '../stores/auth';

export default {
	data() {
		return {
			form: {
				username: '',
				password: '',
			},
			otpCode: '',
		};
	},
	computed: {
		isLoading() {
			const authStore = useAuthStore();
			return authStore.isLoading;
		},
		errors() {
			const authStore = useAuthStore();
			return authStore.errors;
		},
		otpRequired() {
			const authStore = useAuthStore();
			return authStore.otpRequired;
		},
	},
	methods: {
		async handleLogin() {
			const authStore = useAuthStore();
			const formData = {
				username: this.form.username,
				password: this.form.password,
			};
			await authStore.login(formData);
			if (Object.entries(authStore.errors).length){
				this.$toast.error(authStore.errors.detail ?? authStore.errors.message ?? 'Login failed');
			}
			if (authStore.lastResponse && authStore.lastResponse.status < 400){
				this.$toast.success(authStore.lastResponse.data.message);
			}
		},
		async handleOtpConfirmation() {
			const authStore = useAuthStore();
			const success = await authStore.confirmOtp(this.otpCode);

			if (success) {
				this.$toast.success('Login successful');
				router.push('/');
			} else {
				this.$toast.error(authStore.errors?.detail ?? authStore.errors?.message ?? 'Invalid OTP code');
			}
		},
	},
};
</script>

<style scoped>
button {
	display: block;
	margin-top: 1rem;
}
</style>
