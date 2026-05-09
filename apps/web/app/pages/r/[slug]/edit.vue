<script setup lang="ts">
import type { RecipeFormData, RecipeFormSubmitData } from "~~/types/forms";

definePageMeta({ middleware: "auth" });

const route = useRoute();

const slug = route.params.slug as string;

const { data: recipe, error: fetchError } = await useAsyncData(
	`recipe:edit:${slug}`,
	async () => {
		const { data, error: apiError } = await $api.GET("/api/recipes/{slug}", {
			params: { path: { slug } },
		});
		if (apiError) throw apiError;
		return data;
	},
);

if (fetchError.value || !recipe.value) {
	throw createError({ statusCode: 404, statusMessage: "Recipe not found" });
}

const initial = computed<Partial<RecipeFormData> | undefined>(() => {
	const r = recipe.value;
	if (!r) return undefined;
	return {
		title: r.title,
		description: r.description ?? "",
		servings: r.servings,
		prep_time_minutes: r.prep_time_minutes,
		cook_time_minutes: r.cook_time_minutes,
		source_url: r.source_url ?? "",
		is_public: r.is_public,
		image_url: r.image_url ?? "",
		image_public_id: r.image_public_id ?? "",
		category_item_ids: r.category_items.map((c) => c.id),
		tag_ids: r.tags.map((t) => t.id),
		ingredients: r.ingredients.map((ing, idx) => ({
			position: ing.position ?? idx + 1,
			quantity: ing.quantity ?? "",
			unit: ing.unit ?? "",
			name: ing.name,
			notes: ing.notes ?? "",
		})),
		steps: r.steps.map((s, idx) => ({
			position: Number(s.position ?? idx + 1),
			text: String(s.text ?? ""),
		})),
	};
});

const error = ref("");

async function handleSubmit(data: RecipeFormSubmitData) {
	if (!recipe.value) return;
	error.value = "";
	const { error: apiError } = await $api.PATCH("/api/recipes/{recipe_id}", {
		params: { path: { recipe_id: recipe.value.id } },
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
	if (apiError) {
		const detail = (apiError as { detail?: string })?.detail;
		error.value = detail ?? "Failed to save recipe.";
		return;
	}
	await navigateTo(`/r/${recipe.value.slug}`);
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 md:px-6 py-8">
    <h1 class="font-display font-black text-2xl mb-6">Edit Recipe</h1>
    <p v-if="error" class="mb-4 font-mono text-xs text-dish-secondary">{{ error }}</p>
    <RecipeForm
      v-if="initial"
      :initial="initial"
      submit-label="Save Changes"
      @submit="handleSubmit"
    />
  </div>
</template>
