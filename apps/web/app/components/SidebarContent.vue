<script setup lang="ts">
import { PhCheck } from "@phosphor-icons/vue";
import type { components } from "~~/types/api";

type Category = components["schemas"]["CategoryOut"];
type CategoryItem =
	components["schemas"]["app__routers__categories__CategoryItemOut"];
type Tag = components["schemas"]["TagOut"];

defineProps<{
	sortedCategories: Category[];
	sortedItems: (cat: Category) => CategoryItem[];
	tags: Tag[];
	activeItemIds: Set<string>;
	activeTagIds: Set<string>;
	showStatus?: boolean;
	status: "published" | "draft" | "all";
}>();

const emit = defineEmits<{
	toggleItem: [id: string];
	toggleTag: [id: string];
	setStatus: [s: "published" | "draft" | "all"];
}>();

const CATEGORY_GROUP_LABELS: Record<string, string> = {
	dish_type: "Dish Type",
	mood: "Mood",
	protein: "Protein",
};
</script>

<template>
  <div class="space-y-6">

    <!-- Status (owner /me page only) -->
    <div v-if="showStatus">
      <p class="dish-section-label mb-2">Status</p>
      <div class="space-y-1">
        <button
          v-for="opt in (['all', 'published', 'draft'] as const)"
          :key="opt"
          type="button"
          class="flex items-center gap-2.5 w-full py-0.5 text-left group"
          @click="emit('setStatus', opt)"
        >
          <span
            class="w-3.5 h-3.5 border shrink-0 flex items-center justify-center transition-colors"
            :class="status === opt
              ? 'bg-dish-fg border-dish-fg'
              : 'border-dish-fg/40 group-hover:border-dish-fg'"
          >
            <PhCheck v-if="status === opt" class="w-2.5 h-2.5 text-white" :weight="'bold'" />
          </span>
          <span
            class="text-sm transition-colors"
            :class="status === opt ? 'text-dish-fg font-medium' : 'text-dish-fg group-hover:text-dish-fg'"
          >
            {{ opt.charAt(0).toUpperCase() + opt.slice(1) }}
          </span>
        </button>
      </div>
    </div>

    <!-- Category groups — checkbox style with icons -->
    <div v-for="cat in sortedCategories" :key="cat.id">
      <p class="dish-section-label mb-2">
        {{ CATEGORY_GROUP_LABELS[cat.id] ?? cat.id.replace('_', ' ') }}
      </p>
      <div class="space-y-1">
        <button
          v-for="item in sortedItems(cat)"
          :key="item.id"
          type="button"
          class="flex items-center gap-2.5 w-full py-0.5 text-left group"
          @click="emit('toggleItem', item.id)"
        >
          <!-- Checkbox -->
          <span
            class="w-3.5 h-3.5 border shrink-0 flex items-center justify-center transition-colors"
            :class="activeItemIds.has(item.id)
              ? 'bg-dish-fg border-dish-fg'
              : 'border-dish-fg/40 group-hover:border-dish-fg'"
          >
            <PhCheck v-if="activeItemIds.has(item.id)" class="w-2.5 h-2.5 text-white" :weight="'bold'" />
          </span>
          <!-- Icon -->
          <span class="text-sm leading-none" aria-hidden="true">{{ itemIcon(item.id) }}</span>
          <!-- Label -->
          <span
            class="text-sm transition-colors"
            :class="activeItemIds.has(item.id) ? 'text-dish-fg font-medium' : 'text-dish-fg group-hover:text-dish-fg'"
          >
            {{ itemLabel(item.id) }}
          </span>
        </button>
      </div>
    </div>

    <!-- Tags — rounded pills, visually distinct from category checkboxes -->
    <div v-if="tags.length > 0">
      <p class="dish-section-label mb-2">Tags</p>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="tag in tags"
          :key="tag.id"
          type="button"
          class="px-2.5 py-0.5 font-mono text-xs border transition-colors rounded-full"
          :class="activeTagIds.has(tag.id)
            ? 'bg-dish-fg text-dish-surface border-dish-fg'
            : 'text-dish-fg border-dish-fg/30 hover:border-dish-fg hover:text-dish-fg'"
          @click="emit('toggleTag', tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>
    </div>

  </div>
</template>
