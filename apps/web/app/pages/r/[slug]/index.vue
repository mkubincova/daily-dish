<script setup lang="ts">
import type { components } from "~~/types/api";

type RecipeOut = components["schemas"]["RecipeOut"];

const route = useRoute();
const config = useRuntimeConfig();
const authStore = useAuthStore();

const favoritesStore = useFavoritesStore();

const { data: recipe, error } = await useFetch<RecipeOut>(
	`${config.public.apiUrl}/recipes/${route.params.slug}`,
	{ credentials: "include" as RequestCredentials },
);

if (recipe.value) favoritesStore.seed([recipe.value]);

if (error.value || !recipe.value) {
	throw createError({ statusCode: 404, statusMessage: "Recipe not found" });
}

const isOwner = computed(() =>
	Boolean(
		authStore.user &&
			recipe.value &&
			authStore.user.id === recipe.value.user_id,
	),
);

async function confirmDelete() {
	if (!recipe.value) return;
	if (!confirm("Delete this recipe? This cannot be undone.")) return;
	await $fetch(`${config.public.apiUrl}/recipes/${recipe.value.id}`, {
		method: "DELETE",
		credentials: "include",
	});
	await navigateTo("/me");
}
</script>

<template>
  <div v-if="recipe" class="max-w-2xl mx-auto">
    <!-- Hero image -->
    <img
      v-if="recipe.image_url"
      :src="recipe.image_url"
      :alt="recipe.title"
      class="w-full h-64 sm:h-80 object-cover rounded-xl mb-6"
    />

    <!-- Title + owner actions -->
    <div class="flex items-start justify-between gap-4 mb-4">
      <div class="flex items-start gap-3 min-w-0">
        <h1 class="text-3xl font-bold text-gray-900 leading-tight">{{ recipe.title }}</h1>
        <FavoriteButton :recipe-id="recipe.id" />
      </div>
      <div v-if="isOwner" class="flex gap-2 shrink-0">
        <NuxtLink
          :to="`/r/${recipe.slug}/edit`"
          class="text-sm border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50"
        >
          Edit
        </NuxtLink>
        <button
          class="text-sm border border-red-300 text-red-600 px-3 py-1.5 rounded-md hover:bg-red-50"
          type="button"
          @click="confirmDelete"
        >
          Delete
        </button>
      </div>
    </div>

    <!-- Meta -->
    <div class="text-sm text-gray-500 mb-6 flex flex-wrap gap-4">
      <span v-if="recipe.servings">{{ recipe.servings }} servings</span>
      <span v-if="recipe.prep_time_minutes">Prep: {{ recipe.prep_time_minutes }} min</span>
      <span v-if="recipe.cook_time_minutes">Cook: {{ recipe.cook_time_minutes }} min</span>
      <span>by {{ recipe.owner.name }}</span>
    </div>

    <p v-if="recipe.description" class="text-gray-700 mb-8 text-lg leading-relaxed">
      {{ recipe.description }}
    </p>

    <!-- Ingredients -->
    <section v-if="recipe.ingredients?.length" class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Ingredients</h2>
      <ul class="space-y-2">
        <li
          v-for="ing in recipe.ingredients"
          :key="ing.id"
          class="flex gap-3 text-base text-gray-800 leading-relaxed"
        >
          <span v-if="ing.quantity || ing.unit" class="font-medium shrink-0">
            {{ ing.quantity }} {{ ing.unit }}
          </span>
          <span>{{ ing.name }}<span v-if="ing.notes" class="text-gray-500">, {{ ing.notes }}</span></span>
        </li>
      </ul>
    </section>

    <!-- Steps -->
    <section v-if="recipe.steps?.length">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Steps</h2>
      <ol class="space-y-6">
        <li
          v-for="step in recipe.steps"
          :key="String(step.position)"
          class="flex gap-4"
        >
          <span class="text-emerald-600 font-bold text-lg shrink-0 mt-0.5">{{ step.position }}.</span>
          <p class="text-base text-gray-800 leading-relaxed">{{ step.text }}</p>
        </li>
      </ol>
    </section>

    <p v-if="recipe.source_url" class="mt-8 text-sm text-gray-400">
      Source: <a :href="recipe.source_url" class="underline" target="_blank" rel="noopener">{{ recipe.source_url }}</a>
    </p>
  </div>
</template>
