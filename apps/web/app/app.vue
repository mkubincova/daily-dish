<script setup lang="ts">
const authStore = useAuthStore();

onMounted(() => {
	authStore.fetchMe();
});
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
