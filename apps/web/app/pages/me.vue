<script setup lang="ts">
import type { components } from "~~/types/api";

type RecipeListItem = components["schemas"]["RecipeListItem"];

definePageMeta({ middleware: "auth" });

const config = useRuntimeConfig();
const route = useRoute();
const { toApiParams } = useRecipeFilters();

const {
	data: recipes,
	pending,
	refresh,
} = await useFetch<RecipeListItem[]>(`${config.public.apiUrl}/recipes/mine`, {
	credentials: "include" as RequestCredentials,
	query: computed(() => toApiParams()),
});

watch(
	() => route.query,
	() => refresh(),
);

async function deleteRecipe(id: string) {
	if (!confirm("Delete this recipe? This cannot be undone.")) return;
	await $fetch(`${config.public.apiUrl}/recipes/${id}`, {
		method: "DELETE",
		credentials: "include",
	});
	refresh();
}
</script>

<template>
  <div class="lg:h-[calc(100vh-3.5rem)] lg:overflow-hidden">
    <div class="max-w-6xl mx-auto px-4 md:px-6 py-8 lg:flex lg:gap-8 lg:h-full">
      <CategorySidebar :show-status="true" />

      <div class="flex-1 min-w-0 lg:overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h1 class="font-display font-black text-2xl">My Recipes</h1>
          <NuxtLink to="/r/new" class="dish-btn-primary px-4 py-2">
            + New Recipe
          </NuxtLink>
        </div>

        <div v-if="pending" class="font-mono text-sm text-dish-fg/50 py-8">Loading…</div>
        <div v-else-if="!recipes?.length" class="font-mono text-sm text-dish-fg/50 py-8">
          No recipes found.
        </div>

        <div v-else class="space-y-2">
          <RecipeListItem
            v-for="recipe in recipes"
            :key="recipe.id"
            :recipe="recipe"
            @delete="deleteRecipe"
          />
        </div>
      </div>
    </div>
  </div>
</template>
