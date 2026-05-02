<script setup lang="ts">
import {
	PhCaretDown,
	PhList,
	PhPlus,
	PhSignOut,
	PhUser,
	PhX,
} from "@phosphor-icons/vue";

const authStore = useAuthStore();
const mobileMenuOpen = ref(false);
const userMenuOpen = ref(false);
const userMenuRef = ref<HTMLElement | null>(null);
const route = useRoute();

watch(route, () => {
	mobileMenuOpen.value = false;
	userMenuOpen.value = false;
});

const PROVIDER_LABELS: Record<string, string> = {
	github: "GitHub",
	google: "Google",
};

function providerLabel(p: string | undefined): string {
	if (!p) return "";
	return PROVIDER_LABELS[p] ?? p;
}

function onDocumentClick(event: MouseEvent) {
	if (!userMenuOpen.value) return;
	const target = event.target as Node | null;
	if (userMenuRef.value && target && !userMenuRef.value.contains(target)) {
		userMenuOpen.value = false;
	}
}

function onKeydown(event: KeyboardEvent) {
	if (event.key === "Escape") userMenuOpen.value = false;
}

onMounted(() => {
	document.addEventListener("click", onDocumentClick);
	document.addEventListener("keydown", onKeydown);
});
onBeforeUnmount(() => {
	document.removeEventListener("click", onDocumentClick);
	document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div class="min-h-screen bg-dish-bg">
    <header class="bg-dish-bg border-b border-dish-fg/10 sticky top-0 z-40">
      <div
        class="max-w-6xl mx-auto px-4 md:px-6 h-14 flex items-center justify-between"
      >
        <NuxtLink
          to="/"
          class="font-display italic font-bold text-xl text-dish-fg tracking-tight"
        >
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
              class="dish-btn-primary px-3 py-2 flex items-center gap-1.5"
            >
              <PhPlus class="w-3.5 h-3.5" />
              New Recipe
            </NuxtLink>
            <div ref="userMenuRef" class="relative">
              <button
                type="button"
                class="flex items-center gap-2 text-sm text-dish-fg hover:text-dish-primary transition-colors"
                :aria-expanded="userMenuOpen"
                aria-haspopup="menu"
                @click="userMenuOpen = !userMenuOpen"
              >
                <img
                  v-if="authStore.user?.avatar_url"
                  :src="authStore.user.avatar_url"
                  :alt="authStore.user.name"
                  class="w-7 h-7 rounded-full object-cover border border-dish-fg/15"
                />
                <span
                  v-else
                  class="w-7 h-7 rounded-full bg-dish-surface border border-dish-fg/15 flex items-center justify-center"
                >
                  <PhUser class="w-3.5 h-3.5 text-dish-fg/60" />
                </span>
                <span class="font-medium">{{ authStore.user?.name }}</span>
                <PhCaretDown
                  class="w-3 h-3 text-dish-fg/60 transition-transform duration-200"
                  :class="{ 'rotate-180': userMenuOpen }"
                />
              </button>

              <Transition name="slide-down">
                <div
                  v-if="userMenuOpen"
                  class="absolute right-0 mt-2 w-64 bg-dish-surface border border-dish-fg/10 shadow-lg overflow-hidden"
                  role="menu"
                >
                  <div class="px-4 py-3 border-b border-dish-fg/10">
                    <p
                      class="font-display font-bold text-sm text-dish-fg truncate"
                    >
                      {{ authStore.user?.name }}
                    </p>
                    <p class="text-xs text-dish-fg/70 truncate mt-0.5">
                      {{ authStore.user?.email }}
                    </p>
                    <p
                      v-if="authStore.user?.provider"
                      class="font-mono text-[10px] uppercase tracking-widest text-dish-fg/50 mt-2"
                    >
                      via {{ providerLabel(authStore.user.provider) }}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-dish-fg hover:text-dish-primary transition-colors text-left"
                    role="menuitem"
                    @click="authStore.logout()"
                  >
                    <PhSignOut class="w-4 h-4" />
                    Sign out
                  </button>
                </div>
              </Transition>
            </div>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="dish-btn-primary px-3 py-1.5">
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
          <template v-if="authStore.isAuthenticated">
            <div
              class="flex items-center gap-3 pb-3 mb-2 border-b border-dish-fg/10"
            >
              <img
                v-if="authStore.user?.avatar_url"
                :src="authStore.user.avatar_url"
                :alt="authStore.user.name"
                class="w-10 h-10 rounded-full object-cover border border-dish-fg/15 shrink-0"
              />
              <span
                v-else
                class="w-10 h-10 rounded-full bg-dish-surface border border-dish-fg/15 flex items-center justify-center shrink-0"
              >
                <PhUser class="w-5 h-5 text-dish-fg/60" />
              </span>
              <div class="min-w-0">
                <p class="font-display font-bold text-sm text-dish-fg truncate">
                  {{ authStore.user?.name }}
                </p>
                <p class="text-xs text-dish-fg/70 truncate">
                  {{ authStore.user?.email }}
                </p>
                <p
                  v-if="authStore.user?.provider"
                  class="font-mono text-[10px] uppercase tracking-widest text-dish-fg/50 mt-0.5"
                >
                  via {{ providerLabel(authStore.user.provider) }}
                </p>
              </div>
            </div>
          </template>
          <NuxtLink
            to="/"
            class="block py-2 text-sm text-dish-fg hover:text-dish-primary"
            @click="mobileMenuOpen = false"
            >Recipes</NuxtLink
          >
          <template v-if="authStore.isAuthenticated">
            <NuxtLink
              to="/me"
              class="block py-2 text-sm text-dish-fg hover:text-dish-primary"
              @click="mobileMenuOpen = false"
              >My Recipes</NuxtLink
            >
            <NuxtLink
              to="/favorites"
              class="block py-2 text-sm text-dish-fg hover:text-dish-primary"
              @click="mobileMenuOpen = false"
              >Favorites</NuxtLink
            >
            <NuxtLink
              to="/r/new"
              class="dish-btn-primary inline-block px-3 py-1.5 mt-1"
              @click="mobileMenuOpen = false"
              >+ New Recipe</NuxtLink
            >
            <button
              type="button"
              class="flex items-center gap-2 py-2 text-sm text-dish-fg/60 hover:text-dish-fg w-full text-left"
              @click="authStore.logout()"
            >
              <PhSignOut class="w-4 h-4" />
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
