import { defineStore } from "pinia";
import type { components } from "~~/types/api";

type User = components["schemas"]["UserPublic"];

export const useAuthStore = defineStore("auth", () => {
	const user = ref<User | null>(null);
	const pending = ref(false);

	const isAuthenticated = computed(() => user.value !== null);

	async function fetchMe() {
		pending.value = true;
		try {
			const { data, error } = await $api.GET("/api/auth/me");
			if (error) throw error;
			user.value = data;
		} catch {
			user.value = null;
		} finally {
			pending.value = false;
		}
	}

	async function logout() {
		await $api.POST("/api/auth/logout").catch(() => {});
		user.value = null;
		await navigateTo("/");
	}

	function loginWithGithub() {
		window.location.href = "/api/auth/github/login";
	}

	function loginWithGoogle() {
		window.location.href = "/api/auth/google/login";
	}

	return {
		user,
		pending,
		isAuthenticated,
		fetchMe,
		logout,
		loginWithGithub,
		loginWithGoogle,
	};
});
