<script setup lang="ts">
import { PhHeart } from "@phosphor-icons/vue";

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
    class="w-8 h-8 rounded-full bg-dish-surface flex items-center justify-center shrink-0 shadow-md transition-all duration-150 hover:scale-110 active:scale-90"
    :class="active ? 'text-dish-error' : 'text-dish-error/40 hover:text-dish-error'"
    @click="handleClick"
  >
    <PhHeart class="w-4 h-4" :weight="active ? 'fill' : 'regular'" />
  </button>
</template>
