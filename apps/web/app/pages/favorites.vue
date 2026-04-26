<script setup lang="ts">
import type { components } from "~~/types/api";

type PaginatedRecipes = components["schemas"]["PaginatedRecipes"];

definePageMeta({ middleware: "auth" });

const config = useRuntimeConfig();
const route = useRoute();
const { toApiParams } = useRecipeFilters();
const favoritesStore = useFavoritesStore();

const {
	data: feed,
	pending,
	refresh,
} = await useFetch<PaginatedRecipes>(
	`${config.public.apiUrl}/users/me/favorites`,
	{
		credentials: "include" as RequestCredentials,
		query: computed(() => toApiParams()),
	},
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

// Filter through the store so unfavoriting instantly removes the card
// without waiting for a network refetch.
const visibleRecipes = computed(() =>
	(feed.value?.items ?? []).filter((r) => favoritesStore.isFavorited(r.id)),
);
</script>

<template>
  <div class="lg:h-[calc(100vh-3.5rem)] lg:overflow-hidden">
    <div class="max-w-6xl mx-auto px-4 md:px-6 py-8 lg:flex lg:gap-8 lg:h-full">
      <CategorySidebar />

      <div class="flex-1 min-w-0 lg:overflow-y-auto">
        <h1 class="font-display font-black text-2xl mb-6">Favorites</h1>

        <div v-if="pending" class="font-mono text-sm text-dish-fg/50 py-8">
          Loading…
        </div>

        <div v-else-if="visibleRecipes.length === 0" class="py-16 text-center">
          <p class="font-display italic text-xl text-dish-fg/50 mb-2">
            No favorites yet.
          </p>
          <p class="font-mono text-xs uppercase tracking-widest text-dish-fg/35">
            Browse
            <NuxtLink to="/" class="text-dish-primary hover:underline">recipes</NuxtLink>
            and tap the heart to save them here.
          </p>
        </div>

        <div
          v-else
          class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-5"
        >
          <RecipeCard
            v-for="(recipe, index) in visibleRecipes"
            :key="recipe.id"
            :recipe="recipe"
            :index="index"
            show-dish-badges
          />
        </div>
      </div>
    </div>
  </div>
</template>
