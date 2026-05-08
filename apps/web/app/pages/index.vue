<script setup lang="ts">
import type { components } from "~~/types/api";

type Recipe = components["schemas"]["RecipeListItem"];

const route = useRoute();
const { filters } = useRecipeFilters();
const favoritesStore = useFavoritesStore();

const {
	data: feed,
	pending,
	error,
	refresh,
} = await useAsyncData(
	"recipes:list",
	async () => {
		const f = filters.value;
		const { data, error: apiError } = await $api.GET("/api/recipes", {
			params: {
				query: {
					...(f.categoryItems.length > 0 && {
						category_items: f.categoryItems.map((g) => g.join(",")),
					}),
					...(f.tags.length > 0 && { tags: f.tags }),
				},
			},
		});
		if (apiError) throw apiError;
		return data;
	},
	{ watch: [filters] },
);

watch(
	() => route.query,
	() => refresh(),
);

watch(
	feed,
	(val) => {
		if (val?.items) favoritesStore.seed(val.items);
	},
	{ immediate: true },
);

const { tags: allTags, ensureLoaded: ensureTags } = useTags();
onMounted(() => ensureTags());
const tagMap = computed(
	() => new Map(allTags.value.map((t) => [t.id, t.name])),
);

function tagIds(recipe: Recipe): string[] {
	return recipe.tag_ids ?? [];
}

function recipeTags(recipe: Recipe): string[] {
	return tagIds(recipe)
		.map((id) => tagMap.value.get(id))
		.filter((n): n is string => !!n);
}
</script>

<template>
  <HeroBanner />

  <div class="lg:sticky lg:top-14 lg:h-[calc(100vh-3.5rem)] lg:overflow-hidden">
    <div class="max-w-6xl mx-auto px-4 md:px-6 py-8 lg:flex lg:gap-8 lg:h-full">
      <CategorySidebar />

      <div class="flex-1 min-w-0 lg:overflow-y-auto pt-2">
        <div v-if="pending" class="font-mono text-sm text-dish-fg/60 py-8">
          Loading…
        </div>
        <div v-else-if="error" class="font-mono text-sm text-dish-secondary py-8">
          Failed to load recipes.
        </div>
        <div
          v-else-if="feed?.items?.length === 0"
          class="font-mono text-sm text-dish-fg/60 py-8"
        >
          No recipes found.
        </div>

        <div
          v-else
          class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-5"
        >
          <RecipeCard
            v-for="(recipe, index) in feed?.items"
            :key="recipe.id"
            :recipe="recipe"
            :index="index"
            :tag-names="recipeTags(recipe)"
            show-dish-badges
          />
        </div>
      </div>
    </div>
  </div>
</template>
