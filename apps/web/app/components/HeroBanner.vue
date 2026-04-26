<script setup lang="ts">
const authStore = useAuthStore();
</script>

<template>
  <div
    class="relative overflow-hidden bg-dish-primary border-b border-dish-fg/20"
  >
    <!-- Monochromatic blob texture within the solid color -->
    <div class="absolute inset-0 pointer-events-none">
      <div
        class="blob absolute bg-dish-primary-l"
        style="
          width: 600px;
          height: 560px;
          top: -240px;
          left: -180px;
          opacity: 0.55;
          border-radius: 54% 46% 62% 38% / 48% 56% 44% 52%;
        "
      />
      <div
        class="blob absolute bg-dish-primary-d"
        style="
          width: 340px;
          height: 380px;
          top: -60px;
          left: -30px;
          opacity: 0.45;
          border-radius: 42% 58% 48% 52% / 60% 40% 58% 42%;
        "
      />
      <div
        class="blob absolute bg-dish-primary-d"
        style="
          width: 500px;
          height: 560px;
          top: 50%;
          right: -160px;
          transform: translateY(-55%);
          opacity: 0.4;
          border-radius: 48% 52% 38% 62% / 56% 44% 62% 38%;
        "
      />
      <div
        class="blob absolute bg-dish-primary-l"
        style="
          width: 420px;
          height: 460px;
          bottom: -220px;
          left: 32%;
          opacity: 0.45;
          border-radius: 62% 38% 54% 46% / 44% 60% 40% 56%;
        "
      />
    </div>

    <!-- Newspaper-cutout text: each line is its own strip -->
    <div class="relative z-10 max-w-6xl mx-auto px-4 md:px-6 py-12 md:py-16">
      <div class="flex flex-col items-start gap-6">
        <!-- Eyebrow -->
        <span
          class="font-mono text-[10px] uppercase tracking-widest text-dish-fg/50 bg-dish-surface px-4 py-2 shadow-sm"
        >
          Personal recipe archive
        </span>

        <template v-if="authStore.isAuthenticated">
          <span
            class="font-display font-black text-4xl md:text-5xl lg:text-6xl text-dish-fg bg-dish-surface px-4 py-2 leading-none inline-block rotate-[-2.5deg] shadow-md"
          >
            What are you
          </span>
          <span
            class="font-display font-black text-4xl md:text-5xl lg:text-6xl italic text-dish-primary bg-dish-surface px-4 py-2 leading-none inline-block rotate-[1.8deg] ml-16 shadow-md"
          >
            cooking today?
          </span>
        </template>

        <template v-else>
          <span
            class="font-display font-black text-4xl md:text-5xl lg:text-6xl text-dish-fg bg-dish-surface px-4 py-2 leading-none inline-block rotate-[-2.5deg] shadow-md"
          >
            Discover recipes
          </span>
          <span
            class="font-display font-black text-4xl md:text-5xl lg:text-6xl italic text-dish-primary bg-dish-surface px-4 py-2 leading-none inline-block rotate-[1.8deg] ml-16 shadow-md"
          >
            worth making.
          </span>
        </template>
      </div>
    </div>
  </div>
</template>
