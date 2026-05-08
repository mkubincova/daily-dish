import type { components } from "~~/types/api";

type Category = components["schemas"]["CategoryOut"];

export function useCategories() {
	const categories = useState<Category[]>("categories", () => []);
	const loaded = useState<boolean>("categories:loaded", () => false);

	async function fetch() {
		if (loaded.value) return;
		const { data, error } = await $api.GET("/api/categories");
		if (error) throw error;
		categories.value = data;
		loaded.value = true;
	}

	return { categories, fetch };
}
