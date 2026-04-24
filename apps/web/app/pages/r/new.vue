<script setup lang="ts">
import type { components } from "~~/types/api";
import type { RecipeFormSubmitData } from "~~/types/forms";

type RecipeOut = components["schemas"]["RecipeOut"];

definePageMeta({ middleware: "auth" });

const config = useRuntimeConfig();
const error = ref("");

async function handleSubmit(data: RecipeFormSubmitData) {
	error.value = "";
	try {
		const recipe = await $fetch<RecipeOut>(`${config.public.apiUrl}/recipes`, {
			method: "POST",
			credentials: "include",
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
		await navigateTo(`/r/${recipe.slug}`);
	} catch (e) {
		const detail = (e as { data?: { detail?: string } })?.data?.detail;
		error.value = detail ?? "Failed to save recipe.";
	}
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">New Recipe</h1>
    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    <RecipeForm submit-label="Create Recipe" @submit="handleSubmit" />
  </div>
</template>
