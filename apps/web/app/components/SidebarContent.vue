<script setup lang="ts">
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
	itemLabel: (id: string) => string;
}>();

const emit = defineEmits<{
	toggleItem: [id: string];
	toggleTag: [id: string];
	setStatus: [s: "published" | "draft" | "all"];
}>();
</script>

<template>
  <div class="space-y-5">
    <!-- Status group (owner /me only) -->
    <div v-if="showStatus">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Status</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in (['all', 'published', 'draft'] as const)"
          :key="opt"
          type="button"
          class="px-3 py-1 rounded-full text-sm border transition-colors"
          :class="status === opt
            ? 'bg-emerald-600 text-white border-emerald-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-emerald-400'"
          @click="emit('setStatus', opt)"
        >
          {{ opt.charAt(0).toUpperCase() + opt.slice(1) }}
        </button>
      </div>
    </div>

    <!-- Category sections -->
    <div v-for="cat in sortedCategories" :key="cat.id">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">
        {{ cat.id.replace('_', ' ') }}
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="item in sortedItems(cat)"
          :key="item.id"
          type="button"
          class="px-3 py-1 rounded-full text-sm border transition-colors"
          :class="activeItemIds.has(item.id)
            ? 'bg-emerald-600 text-white border-emerald-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-emerald-400'"
          @click="emit('toggleItem', item.id)"
        >
          {{ itemLabel(item.id) }}
        </button>
      </div>
    </div>

    <!-- Tags section -->
    <div v-if="tags.length > 0">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Tags</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tag in tags"
          :key="tag.id"
          type="button"
          class="px-3 py-1 rounded-full text-sm border transition-colors"
          :class="activeTagIds.has(tag.id)
            ? 'bg-violet-600 text-white border-violet-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-violet-400'"
          @click="emit('toggleTag', tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>
    </div>
  </div>
</template>
