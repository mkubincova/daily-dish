<script setup lang="ts">
import { PhFunnel, PhX } from "@phosphor-icons/vue";
import type { components } from "~~/types/api";

type Category = components["schemas"]["CategoryOut"];

const props = defineProps<{
	showStatus?: boolean;
}>();

const CATEGORY_CONFIG: Record<
	string,
	{ label: string; icon: string; order: number }
> = {
	dish_type: { label: "Dish Type", icon: "🍽️", order: 0 },
	mood: { label: "Mood", icon: "😋", order: 1 },
	protein: { label: "Protein", icon: "🥩", order: 2 },
};

const { categories, fetch: fetchCategories } = useCategories();
const { tags, ensureLoaded: ensureTags } = useTags();
const { filters, toggleCategoryItem, toggleTag, setStatus } =
	useRecipeFilters();

onMounted(() => {
	fetchCategories();
	ensureTags();
});

const sortedCategories = computed<Category[]>(() =>
	[...categories.value].sort((a, b) => {
		const ao = CATEGORY_CONFIG[a.id]?.order ?? 99;
		const bo = CATEGORY_CONFIG[b.id]?.order ?? 99;
		return ao - bo;
	}),
);

function sortedItems(cat: Category) {
	return [...cat.items].sort((a, b) =>
		itemLabel(a.id).localeCompare(itemLabel(b.id)),
	);
}

const activeItemIds = computed<Set<string>>(
	() => new Set(filters.value.categoryItems.flat()),
);
const activeTagIds = computed<Set<string>>(() => new Set(filters.value.tags));

const drawerOpen = ref(false);
</script>

<template>
  <!-- Desktop sidebar -->
  <aside class="hidden lg:block w-52 shrink-0 overflow-y-auto">
    <div>
      <p class="dish-section-label mb-4">Filter</p>
      <SidebarContent
        :sorted-categories="sortedCategories"
        :sorted-items="sortedItems"
        :tags="tags"
        :active-item-ids="activeItemIds"
        :active-tag-ids="activeTagIds"
        :show-status="props.showStatus"
        :status="filters.status"
        @toggle-item="toggleCategoryItem"
        @toggle-tag="toggleTag"
        @set-status="setStatus"
      />
    </div>
  </aside>

  <!-- Mobile: FAB + bottom drawer -->
  <div class="lg:hidden">
    <button
      type="button"
      class="dish-btn-primary fixed bottom-6 right-6 z-40 w-12 h-12 flex items-center justify-center shadow-lg"
      style="border-radius: 50%"
      aria-label="Open filters"
      @click="drawerOpen = true"
    >
      <PhFunnel class="w-5 h-5" />
    </button>

    <Transition name="fade">
      <div v-if="drawerOpen" class="fixed inset-0 z-40 bg-dish-fg/40" @click="drawerOpen = false" />
    </Transition>

    <Transition name="slide-up">
      <div v-if="drawerOpen" class="fixed bottom-0 left-0 right-0 z-50 bg-dish-surface max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between px-4 py-3 border-b border-dish-fg/10">
          <span class="font-mono text-xs uppercase tracking-widest font-semibold text-dish-fg">Filters</span>
          <button
            type="button"
            class="text-dish-fg/60 hover:text-dish-fg transition-colors p-1"
            @click="drawerOpen = false"
          >
            <PhX class="w-4 h-4" />
          </button>
        </div>
        <div class="p-4">
          <SidebarContent
            :sorted-categories="sortedCategories"
            :sorted-items="sortedItems"
            :tags="tags"
            :active-item-ids="activeItemIds"
            :active-tag-ids="activeTagIds"
            :show-status="props.showStatus"
            :status="filters.status"
            @toggle-item="toggleCategoryItem"
            @toggle-tag="toggleTag"
            @set-status="setStatus"
          />
        </div>
      </div>
    </Transition>
  </div>
</template>
