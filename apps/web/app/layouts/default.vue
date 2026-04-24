<script setup lang="ts">
const authStore = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <NuxtLink to="/" class="text-xl font-bold text-emerald-600">
          Daily Dish
        </NuxtLink>
        <nav class="flex items-center gap-4">
          <NuxtLink to="/" class="text-sm text-gray-600 hover:text-gray-900">Recipes</NuxtLink>
          <template v-if="authStore.isAuthenticated">
            <NuxtLink to="/me" class="text-sm text-gray-600 hover:text-gray-900">My Recipes</NuxtLink>
            <NuxtLink to="/r/new" class="text-sm bg-emerald-600 text-white px-3 py-1.5 rounded-md hover:bg-emerald-700">
              New Recipe
            </NuxtLink>
            <button
              class="text-sm text-gray-600 hover:text-gray-900"
              type="button"
              @click="authStore.logout()"
            >
              Sign out
            </button>
          </template>
          <template v-else>
            <button
              class="text-sm text-gray-700 border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-100 flex items-center gap-2"
              type="button"
              @click="authStore.loginWithGithub()"
            >
              Sign in with GitHub
            </button>
            <button
              class="text-sm text-white bg-blue-600 px-3 py-1.5 rounded-md hover:bg-blue-700"
              type="button"
              @click="authStore.loginWithGoogle()"
            >
              Sign in with Google
            </button>
          </template>
        </nav>
      </div>
    </header>
    <main class="max-w-5xl mx-auto px-4 py-8">
      <slot />
    </main>
  </div>
</template>
