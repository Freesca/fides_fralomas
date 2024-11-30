<template>
	<div class="register">
		<h2>Register</h2>
		<form @submit.prevent="handleRegister">

			<div class="form-group">
				<label class="form-label" for="email">Email</label>
				<input class="form-control" type="email" v-model="form.email" id="email" required autocomplete="email" />
				<span class="form-text text-danger" v-if="errors.email" v-html="errors.email.join('<br>')"></span>
			</div>
			<div class="form-group">
				<label class="form-label" for="username">Username</label>
				<input class="form-control" type="text" v-model="form.username" id="username" required autocomplete="username" />
				<span class="form-text text-danger" v-if="errors.username" v-html="errors.username.join('<br>')"></span>
			</div>
			<div class="form-group">
				<label class="form-label" for="password">Password</label>
				<input class="form-control" type="password" v-model="form.password" id="password" required autocomplete="new-password" />
				<span class="form-text text-danger" v-if="errors.password" v-html="errors.password.join('<br>')"></span>
			</div>
			<div class="form-group">
				<label class="form-label" for="passwordConfirm">Confirm Password</label>
				<input class="form-control" type="password" v-model="form.passwordConfirm" id="passwordConfirm" required autocomplete="new-password" />
				<span class="form-text text-danger" v-if="errors.passwordConfirm" v-html="errors.passwordConfirm.join('<br>')"></span>
			</div>
			<button v-if="!otpRequired" class="btn btn-success mt-3" type="submit" :disabled="isLoading">Register</button>
		</form>

		<div v-if="otpRequired">
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
import { useAuthStore } from '../stores/auth';

export default {
	data() {
		return {
			form: {
				email: '',
				username: '',
				password: '',
				passwordConfirm: '',
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
		async handleRegister() {
			const authStore = useAuthStore();
			const formData = {
				email: this.form.email,
				username: this.form.username,
				password: this.form.password,
				password_confirm: this.form.passwordConfirm,
			};
			await authStore.register(formData);
		},
		async handleOtpConfirmation() {
			const authStore = useAuthStore();
			const success = await authStore.confirmOtp(this.otpCode);
			if (success) {
				router.push('/');
			}
		},
	},
};
</script>
