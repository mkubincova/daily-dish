<script setup lang="ts">
const props = defineProps<{
	error: { statusCode: number; statusMessage: string };
}>();
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center text-center px-4">
    <p class="text-6xl font-bold text-emerald-600 mb-4">{{ error.statusCode }}</p>
    <h1 class="text-2xl font-semibold text-gray-900 mb-2">{{ error.statusMessage ?? 'Something went wrong' }}</h1>
    <p class="text-gray-500 mb-8">Sorry, we couldn't find what you were looking for.</p>
    <NuxtLink to="/" class="text-emerald-600 underline">Back to recipes</NuxtLink>
  </div>
</template>
