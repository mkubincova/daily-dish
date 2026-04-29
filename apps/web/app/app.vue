<script setup lang="ts">
const authStore = useAuthStore();
const config = useRuntimeConfig();

onMounted(() => {
	authStore.fetchMe();
});

useSeoMeta({
	title: "Daily Dish",
	description:
		"A personal recipe collection — browse public recipes or sign in to save your own.",
	ogTitle: "Daily Dish",
	ogDescription:
		"A personal recipe collection — browse public recipes or sign in to save your own.",
	ogImage: `${config.public.siteUrl}/og-image.png`,
	ogType: "website",
	ogUrl: config.public.siteUrl,
	twitterCard: "summary_large_image",
	twitterTitle: "Daily Dish",
	twitterDescription:
		"A personal recipe collection — browse public recipes or sign in to save your own.",
	twitterImage: `${config.public.siteUrl}/og-image.png`,
});
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
