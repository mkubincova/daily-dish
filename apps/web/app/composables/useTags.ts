import type { components } from "~~/types/api";

type Tag = components["schemas"]["TagOut"];

export function useTags() {
	const config = useRuntimeConfig();
	const tags = useState<Tag[]>("tags", () => []);
	const loaded = useState<boolean>("tags:loaded", () => false);

	async function fetch() {
		const data = await $fetch<Tag[]>(`${config.public.apiUrl}/tags`);
		tags.value = data;
		loaded.value = true;
	}

	async function ensureLoaded() {
		if (!loaded.value) await fetch();
	}

	async function createTag(name: string): Promise<Tag> {
		const tag = await $fetch<Tag>(`${config.public.apiUrl}/tags`, {
			method: "POST",
			body: { name },
			credentials: "include",
		});
		await fetch();
		return tag;
	}

	return { tags, fetch, ensureLoaded, createTag };
}
