import type { components } from "~~/types/api";

type Tag = components["schemas"]["TagOut"];

export function useTags() {
	const tags = useState<Tag[]>("tags", () => []);
	const loaded = useState<boolean>("tags:loaded", () => false);

	async function fetch() {
		const { data, error } = await $api.GET("/api/tags");
		if (error) throw error;
		tags.value = data;
		loaded.value = true;
	}

	async function ensureLoaded() {
		if (!loaded.value) await fetch();
	}

	async function createTag(name: string): Promise<Tag> {
		const { data, error } = await $api.POST("/api/tags", {
			body: { name },
		});
		if (error) throw error;
		await fetch();
		return data;
	}

	return { tags, fetch, ensureLoaded, createTag };
}
