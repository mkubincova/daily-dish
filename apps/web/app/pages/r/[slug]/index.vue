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

const recipeDescription =
	recipe.value.description ?? "A recipe from Daily Dish.";

useSeoMeta({
	title: `${recipe.value.title} · Daily Dish`,
	description: recipeDescription,
	ogTitle: `${recipe.value.title} · Daily Dish`,
	ogDescription: recipeDescription,
	ogUrl: `${config.public.siteUrl}${route.path}`,
	twitterTitle: `${recipe.value.title} · Daily Dish`,
	twitterDescription: recipeDescription,
});

const isOwner = computed(() =>
	Boolean(
		authStore.user &&
			recipe.value &&
			authStore.user.id === recipe.value.user_id,
	),
);

async function confirmDelete() {
	if (!recipe.value) return;
	if (!confirm("Move this recipe to trash?")) return;
	await $fetch(`${config.public.apiUrl}/recipes/${recipe.value.id}`, {
		method: "DELETE",
		credentials: "include",
	});
	await navigateTo("/me");
}

// Category IDs and tag names come directly from the full RecipeOut response
const categoryItemIds = computed<string[]>(
	() => recipe.value?.category_items.map((c) => c.id) ?? [],
);
const tagNames = computed<string[]>(
	() => recipe.value?.tags.map((t) => t.name) ?? [],
);

const formattedDate = computed(() =>
	recipe.value
		? new Date(recipe.value.created_at).toLocaleDateString("en-GB", {
				day: "numeric",
				month: "short",
				year: "numeric",
			})
		: "",
);
</script>

<template>
  <div
    v-if="recipe"
    class="lg:h-[calc(100vh-3.5rem)] lg:flex lg:overflow-hidden"
  >
    <!-- Desktop: fixed image column with favorite overlay -->
    <div
      class="hidden lg:block lg:w-2/5 xl:w-1/2 shrink-0 bg-dish-bg relative overflow-hidden"
    >
      <img
        v-if="recipe.image_url"
        :src="recipe.image_url"
        :alt="recipe.title"
        class="w-full h-full object-cover"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-8xl"
      >
        🍽️
      </div>
      <div class="absolute top-3 right-3">
        <FavoriteButton :recipe-id="recipe.id" />
      </div>
    </div>

    <!-- Scrollable text column (full-width on mobile) -->
    <div class="flex-1 min-w-0 lg:overflow-y-auto">
      <!-- Mobile image/placeholder with favorite overlay -->
      <div
        class="lg:hidden relative w-full aspect-video overflow-hidden bg-dish-bg"
      >
        <img
          v-if="recipe.image_url"
          :src="recipe.image_url"
          :alt="recipe.title"
          class="w-full h-full object-cover"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center text-6xl"
        >
          🍽️
        </div>
        <div class="absolute top-2.5 right-2.5">
          <FavoriteButton :recipe-id="recipe.id" />
        </div>
      </div>

      <div class="px-4 md:px-8 lg:px-10 py-8">
        <!-- Title + owner actions -->
        <div class="flex items-start justify-between gap-4 mb-1">
          <h1
            class="font-display font-black text-3xl md:text-4xl leading-tight text-dish-fg"
          >
            {{ recipe.title }}
          </h1>
          <div v-if="isOwner" class="flex gap-2 shrink-0">
            <NuxtLink
              :to="`/r/${recipe.slug}/edit`"
              class="dish-btn-secondary px-3 py-1.5"
            >
              Edit
            </NuxtLink>
            <button
              type="button"
              class="dish-btn-danger px-3 py-1.5"
              @click="confirmDelete"
            >
              Delete
            </button>
          </div>
        </div>

        <!-- Author + date -->
        <p
          class="font-mono text-[10px] uppercase tracking-widest text-dish-fg/50 mb-6"
        >
          by {{ recipe.owner.name }} &middot; {{ formattedDate }}
        </p>

        <!-- Newspaper-cutout stat boxes -->
        <div
          v-if="
            recipe.servings ||
            recipe.prep_time_minutes ||
            recipe.cook_time_minutes
          "
          class="flex flex-wrap gap-3 mb-8"
        >
          <div
            v-if="recipe.servings"
            class="bg-dish-surface px-4 py-3 shadow-md -rotate-1 shrink-0"
          >
            <p
              class="font-mono text-[9px] uppercase tracking-widest text-dish-fg/50 mb-1"
            >
              Serves
            </p>
            <p
              class="font-display font-black text-2xl text-dish-fg leading-none"
            >
              {{ recipe.servings }}
            </p>
          </div>
          <div
            v-if="recipe.prep_time_minutes"
            class="bg-dish-surface px-4 py-3 shadow-md rotate-1 shrink-0"
          >
            <p
              class="font-mono text-[9px] uppercase tracking-widest text-dish-fg/50 mb-1"
            >
              Prep
            </p>
            <p
              class="font-display font-black text-2xl text-dish-fg leading-none"
            >
              {{ recipe.prep_time_minutes
              }}<span class="text-sm font-sans font-normal ml-0.5">min</span>
            </p>
          </div>
          <div
            v-if="recipe.cook_time_minutes"
            class="bg-dish-surface px-4 py-3 shadow-md -rotate-1 shrink-0"
          >
            <p
              class="font-mono text-[9px] uppercase tracking-widest text-dish-fg/50 mb-1"
            >
              Cook
            </p>
            <p
              class="font-display font-black text-2xl text-dish-fg leading-none"
            >
              {{ recipe.cook_time_minutes
              }}<span class="text-sm font-sans font-normal ml-0.5">min</span>
            </p>
          </div>
        </div>

        <!-- Categories -->
        <div
          v-if="categoryItemIds.length"
          class="flex flex-wrap gap-1.5"
          :class="tagNames.length ? 'mb-2' : 'mb-6'"
        >
          <span
            v-for="id in categoryItemIds"
            :key="id"
            class="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest border border-dish-fg/25 text-dish-fg px-2.5 py-1"
          >
            <span aria-hidden="true">{{ itemIcon(id) }}</span>
            {{ itemLabel(id) }}
          </span>
        </div>

        <!-- Tags -->
        <div v-if="tagNames.length" class="flex flex-wrap gap-1 mb-6">
          <span v-for="tag in tagNames" :key="tag" class="dish-tag">{{
            tag
          }}</span>
        </div>

        <!-- Description -->
        <p
          v-if="recipe.description"
          class="font-display italic text-lg text-dish-fg mb-8 leading-relaxed"
        >
          {{ recipe.description }}
        </p>

        <!-- Ingredients -->
        <section v-if="recipe.ingredients?.length" class="mb-10">
          <h2
            class="font-display font-black text-xl mb-4 pb-2 border-b border-dish-fg/15"
          >
            Ingredients
          </h2>
          <ul class="space-y-2">
            <li
              v-for="ing in recipe.ingredients"
              :key="ing.id"
              class="flex gap-3 leading-relaxed"
            >
              <span
                v-if="ing.quantity || ing.unit"
                class="font-mono text-sm text-dish-fg/60 shrink-0 w-20"
              >
                {{ ing.quantity }} {{ ing.unit }}
              </span>
              <span class="text-sm text-dish-fg">
                {{ ing.name
                }}<span v-if="ing.notes" class="text-dish-fg/60"
                  >, {{ ing.notes }}</span
                >
              </span>
            </li>
          </ul>
        </section>

        <!-- Steps -->
        <section v-if="recipe.steps?.length" class="mb-10">
          <h2
            class="font-display font-black text-xl mb-4 pb-2 border-b border-dish-fg/15"
          >
            Steps
          </h2>
          <ol class="space-y-6">
            <li
              v-for="step in recipe.steps"
              :key="String(step.position)"
              class="flex gap-4"
            >
              <span
                class="font-display font-black text-dish-primary text-xl shrink-0 w-6 mt-0.5"
                >{{ step.position }}.</span
              >
              <p class="text-dish-fg leading-relaxed">{{ step.text }}</p>
            </li>
          </ol>
        </section>

        <!-- Source -->
        <p
          v-if="recipe.source_url"
          class="font-mono text-xs text-dish-fg/60 uppercase tracking-widest"
        >
          Source:
          <a
            :href="recipe.source_url"
            class="underline hover:text-dish-primary transition-colors"
            target="_blank"
            rel="noopener"
            >{{ recipe.source_url }}</a
          >
        </p>
      </div>
    </div>
  </div>
</template>
