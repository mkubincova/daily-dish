<script setup lang="ts">
const props = defineProps<{
	error: { statusCode: number; statusMessage: string };
}>();
</script>

<template>
  <div class="min-h-screen bg-dish-bg flex flex-col items-center justify-center text-center px-4">
    <p class="font-display font-black text-8xl text-dish-primary mb-4">{{ error.statusCode }}</p>
    <h1 class="font-display font-black text-2xl text-dish-fg mb-2">{{ error.statusMessage ?? 'Something went wrong' }}</h1>
    <p class="font-mono text-sm text-dish-fg/50 mb-8">Sorry, we couldn't find what you were looking for.</p>
    <NuxtLink to="/" class="dish-btn-primary px-4 py-2">Back to recipes</NuxtLink>
  </div>
</template>
