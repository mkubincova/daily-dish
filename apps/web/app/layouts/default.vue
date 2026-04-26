<script setup lang="ts">
import { PhList, PhX } from "@phosphor-icons/vue";

const authStore = useAuthStore();
const mobileMenuOpen = ref(false);
const route = useRoute();
watch(route, () => {
	mobileMenuOpen.value = false;
});
</script>

<template>
  <div class="min-h-screen bg-dish-bg">

    <header class="bg-dish-bg border-b border-dish-fg/10 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-4 md:px-6 h-14 flex items-center justify-between">

        <NuxtLink to="/" class="font-display italic font-bold text-xl text-dish-fg tracking-tight">
          Daily Dish
        </NuxtLink>

        <!-- Desktop nav -->
        <nav class="hidden md:flex items-center gap-6">
          <NuxtLink
            to="/"
            class="text-sm text-dish-fg hover:text-dish-primary transition-colors"
            active-class="text-dish-primary"
          >
            Recipes
          </NuxtLink>
          <template v-if="authStore.isAuthenticated">
            <NuxtLink
              to="/me"
              class="text-sm text-dish-fg hover:text-dish-primary transition-colors"
              active-class="text-dish-primary"
            >
              My Recipes
            </NuxtLink>
            <NuxtLink
              to="/favorites"
              class="text-sm text-dish-fg hover:text-dish-primary transition-colors"
              active-class="text-dish-primary"
            >
              Favorites
            </NuxtLink>
            <NuxtLink
              to="/r/new"
              class="dish-btn-primary px-3 py-1.5"
            >
              + New Recipe
            </NuxtLink>
            <button
              type="button"
              class="text-sm text-dish-fg/60 hover:text-dish-fg transition-colors"
              @click="authStore.logout()"
            >
              Sign out
            </button>
          </template>
          <template v-else>
            <NuxtLink
              to="/login"
              class="dish-btn-primary px-3 py-1.5"
            >
              Log in
            </NuxtLink>
          </template>
        </nav>

        <!-- Mobile right -->
        <div class="flex md:hidden items-center gap-3">
          <NuxtLink
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="dish-btn-primary px-3 py-1.5"
          >
            Log in
          </NuxtLink>
          <button
            type="button"
            class="text-dish-fg p-1"
            aria-label="Toggle menu"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <PhList v-if="!mobileMenuOpen" class="w-5 h-5" />
            <PhX v-else class="w-5 h-5" />
          </button>
        </div>

      </div>

      <!-- Mobile dropdown -->
      <Transition name="slide-down">
        <div
          v-if="mobileMenuOpen"
          class="md:hidden border-t border-dish-fg/10 bg-dish-bg px-4 py-4 space-y-1"
        >
          <NuxtLink to="/" class="block py-2 text-sm text-dish-fg hover:text-dish-primary" @click="mobileMenuOpen = false">Recipes</NuxtLink>
          <template v-if="authStore.isAuthenticated">
            <NuxtLink to="/me" class="block py-2 text-sm text-dish-fg hover:text-dish-primary" @click="mobileMenuOpen = false">My Recipes</NuxtLink>
            <NuxtLink to="/favorites" class="block py-2 text-sm text-dish-fg hover:text-dish-primary" @click="mobileMenuOpen = false">Favorites</NuxtLink>
            <NuxtLink to="/r/new" class="dish-btn-primary inline-block px-3 py-1.5 mt-1" @click="mobileMenuOpen = false">+ New Recipe</NuxtLink>
            <button
              type="button"
              class="block py-2 text-sm text-dish-fg/60 hover:text-dish-fg w-full text-left"
              @click="authStore.logout()"
            >
              Sign out
            </button>
          </template>
        </div>
      </Transition>
    </header>

    <main>
      <slot />
    </main>

  </div>
</template>
