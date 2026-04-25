import type { components } from "~~/types/api";

type Category = components["schemas"]["CategoryOut"];

export function useCategories() {
	const config = useRuntimeConfig();
	const categories = useState<Category[]>("categories", () => []);
	const loaded = useState<boolean>("categories:loaded", () => false);

	async function fetch() {
		if (loaded.value) return;
		const data = await $fetch<Category[]>(`${config.public.apiUrl}/categories`);
		categories.value = data;
		loaded.value = true;
	}

	return { categories, fetch };
}
