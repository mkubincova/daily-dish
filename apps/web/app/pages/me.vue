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
</script>

<template>
  <div class="flex gap-8">
    <CategorySidebar :show-status="true" />
    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900">My Recipes</h1>
        <NuxtLink
          to="/r/new"
          class="text-sm bg-emerald-600 text-white px-4 py-2 rounded-md hover:bg-emerald-700"
        >
          New Recipe
        </NuxtLink>
      </div>

      <div v-if="pending" class="text-gray-500">Loading…</div>
      <div v-else-if="!recipes?.length" class="text-gray-500">No recipes found.</div>
      <div v-else class="space-y-3">
        <div
          v-for="recipe in recipes"
          :key="recipe.id"
          class="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between gap-4"
        >
          <div class="flex items-center gap-4 min-w-0">
            <img
              v-if="recipe.image_url"
              :src="recipe.image_url"
              :alt="recipe.title"
              class="w-16 h-16 object-cover rounded-md shrink-0"
            />
            <div class="min-w-0">
              <NuxtLink
                :to="`/r/${recipe.slug}`"
                class="font-semibold text-gray-900 hover:underline truncate block"
              >
                {{ recipe.title }}
              </NuxtLink>
              <span
                class="inline-block text-xs mt-1 px-2 py-0.5 rounded-full"
                :class="recipe.is_public ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'"
              >
                {{ recipe.is_public ? 'Public' : 'Draft' }}
              </span>
            </div>
          </div>
          <NuxtLink
            :to="`/r/${recipe.slug}/edit`"
            class="text-sm border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50 shrink-0"
          >
            Edit
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
