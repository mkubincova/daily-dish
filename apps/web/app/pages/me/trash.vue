<script setup lang="ts">
import { PhArrowCounterClockwise, PhTrash } from "@phosphor-icons/vue";
import type { components } from "~~/types/api";

type TrashedRecipeItem = components["schemas"]["TrashedRecipeItem"];

definePageMeta({ middleware: "auth" });

const config = useRuntimeConfig();

const { data: trashed, refresh } = await useFetch<TrashedRecipeItem[]>(
	`${config.public.apiUrl}/recipes/trashed`,
	{ credentials: "include" as RequestCredentials },
);

const restoringId = ref<string | null>(null);
const deletingId = ref<string | null>(null);

async function restoreRecipe(id: string) {
	restoringId.value = id;
	try {
		await $fetch(`${config.public.apiUrl}/recipes/${id}/restore`, {
			method: "POST",
			credentials: "include",
		});
		await refresh();
	} finally {
		restoringId.value = null;
	}
}

async function permanentlyDelete(id: string) {
	if (!confirm("Permanently delete this recipe? This cannot be undone."))
		return;
	deletingId.value = id;
	try {
		await $fetch(`${config.public.apiUrl}/recipes/${id}/permanent`, {
			method: "DELETE",
			credentials: "include",
		});
		await refresh();
	} finally {
		deletingId.value = null;
	}
}

function formatDate(iso: string) {
	return new Date(iso).toLocaleDateString(undefined, {
		year: "numeric",
		month: "short",
		day: "numeric",
	});
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 md:px-6 py-8">
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink
        to="/me"
        class="font-mono text-xs uppercase tracking-widest text-dish-fg/50 hover:text-dish-fg transition-colors"
      >
        ← My Recipes
      </NuxtLink>
    </div>

    <h1 class="font-display font-black text-2xl mb-6">Trash</h1>

    <div v-if="!trashed?.length" class="font-mono text-sm text-dish-fg/50 py-12 text-center">
      Trash is empty.
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="recipe in trashed"
        :key="recipe.id"
        class="flex items-center gap-4 py-3 border-b border-dish-fg/10"
      >
        <img
          v-if="recipe.image_url"
          :src="recipe.image_url"
          alt=""
          class="w-12 h-12 object-cover shrink-0"
        />
        <div
          v-else
          class="w-12 h-12 bg-dish-fg/5 shrink-0"
        />

        <div class="flex-1 min-w-0">
          <p class="font-sans text-sm font-medium truncate">{{ recipe.title }}</p>
          <p class="font-mono text-[10px] uppercase tracking-widest text-dish-fg/40 mt-0.5">
            Deleted {{ formatDate(recipe.deleted_at) }}
          </p>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <button
            type="button"
            class="dish-btn-secondary px-3 py-1.5 flex items-center gap-1.5 text-xs disabled:opacity-50"
            :disabled="restoringId === recipe.id || deletingId === recipe.id"
            @click="restoreRecipe(recipe.id)"
          >
            <PhArrowCounterClockwise class="w-3.5 h-3.5" />
            {{ restoringId === recipe.id ? "Restoring…" : "Recover" }}
          </button>

          <button
            type="button"
            class="dish-btn-danger px-3 py-1.5 flex items-center gap-1.5 text-xs disabled:opacity-50"
            :disabled="restoringId === recipe.id || deletingId === recipe.id"
            @click="permanentlyDelete(recipe.id)"
          >
            <PhTrash class="w-3.5 h-3.5" />
            {{ deletingId === recipe.id ? "Deleting…" : "Delete Permanently" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
