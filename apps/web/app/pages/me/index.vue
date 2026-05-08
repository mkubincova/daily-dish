<script setup lang="ts">
import { PhPlus, PhRecycle } from "@phosphor-icons/vue";

definePageMeta({ middleware: "auth" });

const route = useRoute();
const { filters } = useRecipeFilters();

const {
	data: recipes,
	pending,
	refresh,
} = await useAsyncData(
	"recipes:mine",
	async () => {
		const f = filters.value;
		const { data, error: apiError } = await $api.GET("/api/recipes/mine", {
			params: {
				query: {
					...(f.categoryItems.length > 0 && {
						category_items: f.categoryItems.map((g) => g.join(",")),
					}),
					...(f.tags.length > 0 && { tags: f.tags }),
					...(f.status !== "all" && { status: f.status }),
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

async function deleteRecipe(id: string) {
	if (!confirm("Move this recipe to trash?")) return;
	await $api.DELETE("/api/recipes/{recipe_id}", {
		params: { path: { recipe_id: id } },
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
          <div class="flex items-center gap-2">
            <NuxtLink
              to="/me/trash"
              class="dish-btn-secondary px-3 py-2 flex items-center gap-1.5"
            >
              <PhRecycle class="w-3.5 h-3.5" />
              <span class="font-mono text-xs uppercase tracking-widest"
                >View Trash</span
              >
            </NuxtLink>
            <NuxtLink
              to="/r/new"
              class="dish-btn-primary px-3 py-2 flex items-center gap-1.5"
            >
              <PhPlus class="w-3.5 h-3.5" />
              New Recipe
            </NuxtLink>
          </div>
        </div>

        <div v-if="pending" class="font-mono text-sm text-dish-fg/50 py-8">
          Loading…
        </div>
        <div
          v-else-if="!recipes?.length"
          class="font-mono text-sm text-dish-fg/50 py-8"
        >
          No recipes found.
        </div>

        <div v-else class="space-y-2">
          <RecipeListItem
            v-for="(recipe, index) in recipes"
            :key="recipe.id"
            :recipe="recipe"
            :index="index"
            @delete="deleteRecipe"
          />
        </div>
      </div>
    </div>
  </div>
</template>
