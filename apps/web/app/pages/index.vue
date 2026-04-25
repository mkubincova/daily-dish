<script setup lang="ts">
import type { components } from "~~/types/api";

type PaginatedRecipes = components["schemas"]["PaginatedRecipes"];

const config = useRuntimeConfig();
const route = useRoute();
const { toApiParams } = useRecipeFilters();

const {
	data: feed,
	pending,
	error,
	refresh,
} = await useFetch<PaginatedRecipes>(`${config.public.apiUrl}/recipes`, {
	credentials: "include" as RequestCredentials,
	query: computed(() => toApiParams()),
});

watch(
	() => route.query,
	() => refresh(),
);
</script>

<template>
  <div class="flex gap-8">
    <CategorySidebar />
    <div class="flex-1 min-w-0">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Recipes</h1>

      <div v-if="pending" class="text-gray-500">Loading…</div>
      <div v-else-if="error" class="text-red-600">Failed to load recipes.</div>
      <div v-else-if="feed?.items?.length === 0" class="text-gray-500">No recipes found.</div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="recipe in feed?.items"
          :key="recipe.id"
          :to="`/r/${recipe.slug}`"
          class="block bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow border border-gray-100"
        >
          <img
            v-if="recipe.image_url"
            :src="recipe.image_url"
            :alt="recipe.title"
            class="w-full h-44 object-cover"
          />
          <div v-else class="w-full h-44 bg-emerald-50 flex items-center justify-center">
            <span class="text-4xl">🍽️</span>
          </div>
          <div class="p-4">
            <h2 class="font-semibold text-gray-900 text-lg leading-snug">{{ recipe.title }}</h2>
            <p v-if="recipe.description" class="mt-1 text-sm text-gray-600 line-clamp-2">
              {{ recipe.description }}
            </p>
            <div class="mt-3 flex items-center gap-2 text-xs text-gray-400">
              <span>by {{ recipe.owner.name }}</span>
              <span>·</span>
              <span>{{ new Date(recipe.created_at).toLocaleDateString() }}</span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
