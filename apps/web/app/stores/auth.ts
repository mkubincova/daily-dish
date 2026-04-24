import { defineStore } from "pinia";

interface User {
	id: string;
	email: string;
	name: string;
	avatar_url: string | null;
	provider: string;
}

export const useAuthStore = defineStore("auth", () => {
	const user = ref<User | null>(null);
	const pending = ref(false);

	const isAuthenticated = computed(() => user.value !== null);

	const config = useRuntimeConfig();
	const apiUrl = config.public.apiUrl;

	async function fetchMe() {
		pending.value = true;
		try {
			const data = await $fetch<User>(`${apiUrl}/auth/me`, {
				credentials: "include",
			});
			user.value = data;
		} catch {
			user.value = null;
		} finally {
			pending.value = false;
		}
	}

	async function logout() {
		await $fetch(`${apiUrl}/auth/logout`, {
			method: "POST",
			credentials: "include",
		}).catch(() => {});
		user.value = null;
		await navigateTo("/");
	}

	function loginWithGithub() {
		window.location.href = `${apiUrl}/auth/github/login`;
	}

	function loginWithGoogle() {
		window.location.href = `${apiUrl}/auth/google/login`;
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
