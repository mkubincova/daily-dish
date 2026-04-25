<script setup lang="ts">
const props = defineProps<{
	recipeId: string;
}>();

const authStore = useAuthStore();
const favoritesStore = useFavoritesStore();

const active = computed(() => favoritesStore.isFavorited(props.recipeId));

async function handleClick(e: Event) {
	e.preventDefault();
	e.stopPropagation();
	if (!authStore.isAuthenticated) return;
	await favoritesStore.toggleFavorite(props.recipeId);
}
</script>

<template>
  <button
    v-if="authStore.isAuthenticated"
    type="button"
    :aria-label="active ? 'Remove from favorites' : 'Add to favorites'"
    class="p-1.5 rounded-full transition-colors"
    :class="active ? 'text-red-500 hover:text-red-600' : 'text-gray-300 hover:text-red-400'"
    @click="handleClick"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      class="w-5 h-5"
      :fill="active ? 'currentColor' : 'none'"
      stroke="currentColor"
      stroke-width="2"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
      />
    </svg>
  </button>
</template>
