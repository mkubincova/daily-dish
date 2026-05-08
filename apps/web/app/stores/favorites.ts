import { defineStore } from "pinia";

export const useFavoritesStore = defineStore("favorites", () => {
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
				await $api.DELETE("/api/recipes/{recipe_id}/favorite", {
					params: { path: { recipe_id: recipeId } },
				});
			} else {
				await $api.POST("/api/recipes/{recipe_id}/favorite", {
					params: { path: { recipe_id: recipeId } },
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
