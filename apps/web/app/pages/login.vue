<script setup lang="ts">
import { PhGithubLogo, PhGoogleLogo } from "@phosphor-icons/vue";

const authStore = useAuthStore();
if (authStore.isAuthenticated) await navigateTo("/");
</script>

<template>
  <div class="min-h-[calc(100vh-56px)] bg-dish-primary relative overflow-hidden flex items-center justify-center px-6 py-16">

    <!-- Same blob texture as the hero banner -->
    <div class="absolute inset-0 pointer-events-none">
      <div
        class="blob absolute bg-dish-primary-l"
        style="width:600px;height:560px;top:-240px;left:-180px;opacity:0.55;border-radius:54% 46% 62% 38% / 48% 56% 44% 52%;"
      />
      <div
        class="blob absolute bg-dish-primary-d"
        style="width:340px;height:380px;top:-60px;left:-30px;opacity:0.45;border-radius:42% 58% 48% 52% / 60% 40% 58% 42%;"
      />
      <div
        class="blob absolute bg-dish-primary-d"
        style="width:500px;height:560px;top:50%;right:-160px;transform:translateY(-55%);opacity:0.40;border-radius:48% 52% 38% 62% / 56% 44% 62% 38%;"
      />
      <div
        class="blob absolute bg-dish-primary-l"
        style="width:420px;height:460px;bottom:-220px;left:32%;opacity:0.45;border-radius:62% 38% 54% 46% / 44% 60% 40% 56%;"
      />
    </div>

    <div class="relative z-10 bg-dish-surface w-full max-w-sm shadow-xl p-8">
      <h1 class="font-display font-black text-3xl leading-tight mb-1">Welcome back.</h1>
      <p class="font-display italic text-dish-fg/60 text-base mb-8">Sign in to your recipe collection.</p>

      <div class="space-y-3">
        <button
          type="button"
          class="dish-btn-primary w-full flex items-center justify-center gap-3 py-3 px-4"
          @click="authStore.loginWithGithub()"
        >
          <PhGithubLogo class="w-4 h-4 shrink-0" />
          Continue with GitHub
        </button>

        <button
          type="button"
          class="dish-btn-secondary w-full flex items-center justify-center gap-3 py-3 px-4"
          @click="authStore.loginWithGoogle()"
        >
          <PhGoogleLogo class="w-4 h-4 shrink-0" />
          Continue with Google
        </button>
      </div>

      <p class="mt-8 text-center font-mono text-xs text-dish-fg/40 uppercase tracking-widest">
        Your personal recipe collection
      </p>
    </div>
  </div>
</template>
