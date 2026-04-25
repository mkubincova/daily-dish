<script setup lang="ts">
import type { components } from "~~/types/api";

type Category = components["schemas"]["CategoryOut"];

const props = defineProps<{
	showStatus?: boolean;
}>();

// ── FE-owned display config ──────────────────────────────────────────────────

const CATEGORY_CONFIG: Record<
	string,
	{ label: string; icon: string; order: number }
> = {
	dish_type: { label: "Dish Type", icon: "🍽️", order: 0 },
	mood: { label: "Mood", icon: "😋", order: 1 },
	protein: { label: "Protein", icon: "🥩", order: 2 },
};

const ITEM_CONFIG: Record<string, { label: string }> = {
	soup: { label: "Soup" },
	salad: { label: "Salad" },
	main: { label: "Main Course" },
	side: { label: "Side Dish" },
	dessert: { label: "Dessert" },
	snack: { label: "Snack" },
	light: { label: "Light" },
	vegetarian: { label: "Vegetarian" },
	spicy: { label: "Spicy" },
	hearty: { label: "Hearty" },
	fried: { label: "Fried" },
	beef: { label: "Beef" },
	chicken: { label: "Chicken" },
	pork: { label: "Pork" },
	fish: { label: "Fish" },
	rabbit: { label: "Rabbit" },
	duck: { label: "Duck" },
	turkey: { label: "Turkey" },
	plant_based: { label: "Plant-Based" },
};

function itemLabel(id: string): string {
	return ITEM_CONFIG[id]?.label ?? id;
}

// ── Data ─────────────────────────────────────────────────────────────────────

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

// ── Mobile drawer ─────────────────────────────────────────────────────────────

const drawerOpen = ref(false);
</script>

<template>
  <!-- Desktop sidebar -->
  <aside class="hidden lg:block w-56 shrink-0">
    <SidebarContent
      :sorted-categories="sortedCategories"
      :sorted-items="sortedItems"
      :tags="tags"
      :active-item-ids="activeItemIds"
      :active-tag-ids="activeTagIds"
      :show-status="props.showStatus"
      :status="filters.status"
      :item-label="itemLabel"
      @toggle-item="toggleCategoryItem"
      @toggle-tag="toggleTag"
      @set-status="setStatus"
    />
  </aside>

  <!-- Mobile FAB + drawer -->
  <div class="lg:hidden">
    <!-- FAB anchored bottom-right, persistent during scroll -->
    <button
      type="button"
      class="fixed bottom-6 right-6 z-40 bg-emerald-600 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg hover:bg-emerald-700"
      aria-label="Open filters"
      @click="drawerOpen = true"
    >
      <span class="text-xl">⚙️</span>
    </button>

    <!-- Drawer overlay -->
    <Transition name="fade">
      <div
        v-if="drawerOpen"
        class="fixed inset-0 z-40 bg-black/40"
        @click="drawerOpen = false"
      />
    </Transition>

    <!-- Drawer panel -->
    <Transition name="slide-up">
      <div
        v-if="drawerOpen"
        class="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl max-h-[80vh] overflow-y-auto p-4"
      >
        <div class="flex items-center justify-between mb-4">
          <span class="font-semibold text-gray-800">Filters</span>
          <button
            type="button"
            class="text-gray-500 hover:text-gray-700"
            @click="drawerOpen = false"
          >
            ✕
          </button>
        </div>
        <SidebarContent
          :sorted-categories="sortedCategories"
          :sorted-items="sortedItems"
          :tags="tags"
          :active-item-ids="activeItemIds"
          :active-tag-ids="activeTagIds"
          :show-status="props.showStatus"
          :status="filters.status"
          :item-label="itemLabel"
          @toggle-item="toggleCategoryItem"
          @toggle-tag="toggleTag"
          @set-status="setStatus"
        />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.25s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
</style>
