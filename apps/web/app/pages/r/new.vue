<script setup lang="ts">
import type { RecipeFormSubmitData } from "~~/types/forms";

definePageMeta({ middleware: "auth" });

const error = ref("");

async function handleSubmit(data: RecipeFormSubmitData) {
	error.value = "";
	const { data: recipe, error: apiError } = await $api.POST("/api/recipes", {
		body: {
			...data,
			servings: data.servings || null,
			prep_time_minutes: data.prep_time_minutes || null,
			cook_time_minutes: data.cook_time_minutes || null,
			source_url: data.source_url || null,
			image_url: data.image_url || null,
			image_public_id: data.image_public_id || null,
		},
	});
	if (apiError || !recipe) {
		const detail = (apiError as { detail?: string })?.detail;
		error.value = detail ?? "Failed to save recipe.";
		return;
	}
	await navigateTo(`/r/${recipe.slug}`);
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 md:px-6 py-8">
    <h1 class="font-display font-black text-2xl mb-6">New Recipe</h1>
    <p v-if="error" class="mb-4 font-mono text-xs text-dish-secondary">{{ error }}</p>
    <RecipeForm submit-label="Create Recipe" @submit="handleSubmit" />
  </div>
</template>
