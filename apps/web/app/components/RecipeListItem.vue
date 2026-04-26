<script setup lang="ts">
import type { components } from "~~/types/api";

type RecipeListItem = components["schemas"]["RecipeListItem"];

defineProps<{ recipe: RecipeListItem }>();
const emit = defineEmits<{ delete: [id: string] }>();
</script>

<template>
  <div
    class="bg-dish-surface flex items-center justify-between gap-4 p-3 hover:-translate-y-1.5 hover:shadow-md transition-all duration-300"
  >
    <div class="flex items-center gap-3 min-w-0">
      <img
        v-if="recipe.image_url"
        :src="recipe.image_url"
        :alt="recipe.title"
        class="w-14 h-14 object-cover shrink-0"
      />
      <div
        v-else
        class="w-14 h-14 bg-dish-bg flex items-center justify-center text-2xl shrink-0"
      >
        🍽️
      </div>
      <div class="min-w-0">
        <NuxtLink
          :to="`/r/${recipe.slug}`"
          class="font-display font-bold text-dish-fg hover:text-dish-primary transition-colors truncate block"
        >
          {{ recipe.title }}
        </NuxtLink>
        <span
          class="font-mono text-[10px] uppercase tracking-widest mt-0.5 inline-block"
          :class="recipe.is_public ? 'text-dish-success' : 'text-dish-fg/35'"
        >
          {{ recipe.is_public ? "Public" : "Draft" }}
        </span>
      </div>
    </div>
    <div class="flex gap-2 shrink-0">
      <NuxtLink :to="`/r/${recipe.slug}/edit`" class="dish-btn-secondary px-3 py-1.5">
        Edit
      </NuxtLink>
      <button
        type="button"
        class="dish-btn-danger px-3 py-1.5"
        @click="emit('delete', recipe.id)"
      >
        Delete
      </button>
    </div>
  </div>
</template>
