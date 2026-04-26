<script setup lang="ts">
import type { components } from "~~/types/api";

type Recipe = components["schemas"]["RecipeListItem"];

const props = defineProps<{
	recipe: Recipe;
	index: number;
	tagNames?: string[];
	showDishBadges?: boolean;
	accentBorderTop?: boolean;
}>();

function categoryItemIds(): string[] {
	return props.recipe.category_item_ids ?? [];
}

const cardAccent = computed(() =>
	accentColorForRecipe(categoryItemIds(), props.index),
);

const dishTypeItems = computed(() =>
	categoryItemIds().filter((id) => id in DISH_TYPE_COLORS),
);
</script>

<template>
  <div
    class="group bg-dish-surface overflow-hidden shadow-sm hover:-translate-y-1.5 hover:shadow-md transition-all duration-300"
  >
    <NuxtLink :to="`/r/${recipe.slug}`" class="block">
      <!-- Image / placeholder -->
      <div class="relative w-full h-44 overflow-hidden">
        <img
          v-if="recipe.image_url"
          :src="recipe.image_url"
          :alt="recipe.title"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-4xl"
          :style="{ backgroundColor: `${cardAccent}35` }"
        >
          🍽️
        </div>

        <!-- Overlay: dish-type badges (left) + favorite button (right) -->
        <div class="absolute inset-x-0 top-0 flex items-start justify-between p-2.5">
          <div v-if="showDishBadges" class="flex flex-col gap-1">
            <span
              v-for="itemId in dishTypeItems"
              :key="itemId"
              class="inline-block font-mono text-[9px] uppercase tracking-widest text-white px-2 py-0.5 self-start shadow-sm"
              :style="{ backgroundColor: DISH_TYPE_COLORS[itemId] }"
            >{{ DISH_TYPE_LABELS[itemId] ?? itemLabel(itemId) }}</span>
          </div>
          <div v-else />
          <FavoriteButton :recipe-id="recipe.id" />
        </div>
      </div>

      <!-- Card body -->
      <div
        class="p-4"
        :style="accentBorderTop ? { borderTop: `3px solid ${cardAccent}` } : {}"
      >
        <h2 class="font-display font-bold text-xl leading-snug text-dish-fg">
          {{ recipe.title }}
        </h2>
        <p
          v-if="recipe.description"
          class="mt-1.5 font-display italic text-sm text-dish-fg/80 line-clamp-2 leading-relaxed"
        >
          {{ recipe.description }}
        </p>
        <div v-if="tagNames?.length" class="mt-2.5 flex flex-wrap gap-1">
          <span
            v-for="tag in tagNames"
            :key="tag"
            class="dish-tag"
          >{{ tag }}</span>
        </div>
        <p
          class="mt-3 pt-2.5 border-t border-dish-fg/10 font-mono text-[10px] uppercase tracking-widest text-dish-fg/50"
        >
          {{ recipe.owner.name }} &middot;
          {{
            new Date(recipe.created_at).toLocaleDateString("en-GB", {
              day: "numeric",
              month: "short",
              year: "2-digit",
            })
          }}
        </p>
      </div>
    </NuxtLink>
  </div>
</template>
