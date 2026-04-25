import { defineStore } from "pinia";

export const useFavoritesStore = defineStore("favorites", () => {
	const config = useRuntimeConfig();
	const apiUrl = config.public.apiUrl;

	const favoritedIds = ref<Set<string>>(new Set());

	function seed(recipes: Array<{ id: string; is_favorited?: boolean | null }>) {
		for (const r of recipes) {
			if (r.is_favorited === true) {
				favoritedIds.value.add(r.id);
			} else if (r.is_favorited === false) {
				favoritedIds.value.delete(r.id);
			}
		}
	}

	function isFavorited(recipeId: string): boolean {
		return favoritedIds.value.has(recipeId);
	}

	async function toggleFavorite(recipeId: string): Promise<void> {
		const wasFavorited = favoritedIds.value.has(recipeId);

		// Optimistic update
		if (wasFavorited) {
			favoritedIds.value.delete(recipeId);
		} else {
			favoritedIds.value.add(recipeId);
		}

		try {
			if (wasFavorited) {
				await $fetch(`${apiUrl}/recipes/${recipeId}/favorite`, {
					method: "DELETE",
					credentials: "include",
				});
			} else {
				await $fetch(`${apiUrl}/recipes/${recipeId}/favorite`, {
					method: "POST",
					credentials: "include",
				});
			}
		} catch {
			// Rollback on error
			if (wasFavorited) {
				favoritedIds.value.add(recipeId);
			} else {
				favoritedIds.value.delete(recipeId);
			}
		}
	}

	return { favoritedIds, seed, isFavorited, toggleFavorite };
});
