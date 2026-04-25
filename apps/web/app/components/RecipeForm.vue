<script setup lang="ts">
import type { components } from "~~/types/api";
import type {
	RecipeFormData,
	RecipeFormIngredient,
	RecipeFormStep,
	RecipeFormSubmitData,
} from "~~/types/forms";

type SignedUploadParams = components["schemas"]["SignedUploadParams"];
type Tag = components["schemas"]["TagOut"];
type Category = components["schemas"]["CategoryOut"];

const props = defineProps<{
	initial?: Partial<RecipeFormData>;
	submitLabel?: string;
}>();

const emit = defineEmits<{
	submit: [data: RecipeFormSubmitData];
}>();

const config = useRuntimeConfig();

// ── FE label config (mirrors CategorySidebar) ───────────────────────────────

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

// ── Form state ────────────────────────────────────────────────────────────────

const form = reactive<RecipeFormData>({
	title: props.initial?.title ?? "",
	description: props.initial?.description ?? "",
	servings: props.initial?.servings ?? null,
	prep_time_minutes: props.initial?.prep_time_minutes ?? null,
	cook_time_minutes: props.initial?.cook_time_minutes ?? null,
	source_url: props.initial?.source_url ?? "",
	is_public: props.initial?.is_public ?? true,
	image_url: props.initial?.image_url ?? "",
	image_public_id: props.initial?.image_public_id ?? "",
	category_item_ids: props.initial?.category_item_ids ?? [],
	tag_ids: props.initial?.tag_ids ?? [],
	ingredients: props.initial?.ingredients?.map(
		(i: Partial<RecipeFormIngredient>): RecipeFormIngredient => ({
			position: i.position ?? 0,
			quantity: String(i.quantity ?? ""),
			unit: i.unit ?? "",
			name: i.name ?? "",
			notes: i.notes ?? "",
		}),
	) ?? [{ position: 1, quantity: "", unit: "", name: "", notes: "" }],
	steps: props.initial?.steps?.map(
		(s: Partial<RecipeFormStep>): RecipeFormStep => ({
			position: s.position ?? 0,
			text: s.text ?? "",
		}),
	) ?? [{ position: 1, text: "" }],
});

// ── Categories ────────────────────────────────────────────────────────────────

const { categories, fetch: fetchCategories } = useCategories();
onMounted(() => fetchCategories());

const sortedCategories = computed<Category[]>(() =>
	[...categories.value].sort((a, b) => a.id.localeCompare(b.id)),
);

function toggleCategoryItem(itemId: string) {
	const idx = form.category_item_ids.indexOf(itemId);
	if (idx >= 0) {
		form.category_item_ids.splice(idx, 1);
	} else {
		form.category_item_ids.push(itemId);
	}
}

// ── Tags ──────────────────────────────────────────────────────────────────────

const { tags, ensureLoaded: ensureTags, createTag } = useTags();
onMounted(() => ensureTags());

const tagQuery = ref("");
const tagDropdownOpen = ref(false);
const tagError = ref<string | null>(null);

const selectedTags = computed<Tag[]>(() =>
	tags.value.filter((t) => form.tag_ids.includes(t.id)),
);

const filteredSuggestions = computed<Tag[]>(() => {
	const q = tagQuery.value.trim().toLowerCase();
	if (!q) return [];
	return tags.value
		.filter((t) => t.name.includes(q) && !form.tag_ids.includes(t.id))
		.slice(0, 8);
});

const exactMatch = computed(() => {
	const q = tagQuery.value.trim().toLowerCase();
	return tags.value.some((t) => t.name === q);
});

const showCreateOption = computed(() => {
	const q = tagQuery.value.trim();
	return q.length > 0 && !exactMatch.value;
});

function selectTag(tag: Tag) {
	if (!form.tag_ids.includes(tag.id)) {
		form.tag_ids.push(tag.id);
	}
	tagQuery.value = "";
	tagDropdownOpen.value = false;
}

function removeTag(tagId: string) {
	const idx = form.tag_ids.indexOf(tagId);
	if (idx >= 0) form.tag_ids.splice(idx, 1);
}

function scheduleCloseDropdown() {
	setTimeout(() => {
		tagDropdownOpen.value = false;
	}, 150);
}

async function handleCreateTag() {
	const name = tagQuery.value.trim();
	if (!name) return;
	tagError.value = null;
	try {
		const tag = await createTag(name);
		form.tag_ids.push(tag.id);
		tagQuery.value = "";
		tagDropdownOpen.value = false;
	} catch {
		tagError.value = "Failed to create tag. Try again.";
	}
}

// ── Image upload ──────────────────────────────────────────────────────────────

const uploading = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

async function uploadImage(event: Event) {
	const file = (event.target as HTMLInputElement).files?.[0];
	if (!file) return;
	uploading.value = true;
	try {
		const params = await $fetch<SignedUploadParams>(
			`${config.public.apiUrl}/uploads/sign`,
			{ method: "POST", credentials: "include" },
		);
		const fd = new FormData();
		fd.append("file", file);
		fd.append("api_key", params.api_key);
		fd.append("timestamp", String(params.timestamp));
		fd.append("signature", params.signature);
		fd.append("folder", params.folder);

		const res = await fetch(
			`https://api.cloudinary.com/v1_1/${params.cloud_name}/image/upload`,
			{ method: "POST", body: fd },
		);
		const data = await res.json();
		form.image_url = data.secure_url;
		form.image_public_id = data.public_id;
	} finally {
		uploading.value = false;
	}
}

// ── Ingredients / steps ───────────────────────────────────────────────────────

function addIngredient() {
	form.ingredients.push({
		position: form.ingredients.length + 1,
		quantity: "",
		unit: "",
		name: "",
		notes: "",
	});
}

function removeIngredient(index: number) {
	form.ingredients.splice(index, 1);
	form.ingredients.forEach((ing, i) => {
		ing.position = i + 1;
	});
}

function addStep() {
	form.steps.push({ position: form.steps.length + 1, text: "" });
}

function removeStep(index: number) {
	form.steps.splice(index, 1);
	form.steps.forEach((s, i) => {
		s.position = i + 1;
	});
}

// ── Submit ────────────────────────────────────────────────────────────────────

function handleSubmit() {
	const data: RecipeFormSubmitData = {
		...form,
		ingredients: form.ingredients.map((ing) => ({
			...ing,
			quantity: ing.quantity === "" ? null : ing.quantity,
			unit: ing.unit === "" ? null : ing.unit,
			notes: ing.notes === "" ? null : ing.notes,
		})),
	};
	emit("submit", data);
}
</script>

<template>
  <form class="space-y-6" @submit.prevent="handleSubmit">
    <!-- Basic info -->
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
        <input
          v-model="form.title"
          required
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="e.g. Chocolate Chip Cookies"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
      </div>
    </div>

    <!-- Times & servings -->
    <div class="grid grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Servings</label>
        <input
          v-model.number="form.servings"
          type="number"
          min="1"
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Prep (min)</label>
        <input
          v-model.number="form.prep_time_minutes"
          type="number"
          min="0"
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Cook (min)</label>
        <input
          v-model.number="form.cook_time_minutes"
          type="number"
          min="0"
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
        />
      </div>
    </div>

    <!-- Visibility -->
    <div class="flex items-center gap-3">
      <input
        id="is_public"
        v-model="form.is_public"
        type="checkbox"
        class="rounded"
      />
      <label for="is_public" class="text-sm text-gray-700">Public (visible to everyone)</label>
    </div>

    <!-- Source URL -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Source URL</label>
      <input
        v-model="form.source_url"
        type="url"
        class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
        placeholder="https://..."
      />
    </div>

    <!-- Image upload -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Hero Image</label>
      <img
        v-if="form.image_url"
        :src="form.image_url"
        alt="Recipe hero"
        class="w-full h-48 object-cover rounded-lg mb-2"
      />
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="uploadImage"
      />
      <button
        type="button"
        class="text-sm border border-gray-300 px-3 py-2 rounded-md hover:bg-gray-50 flex items-center gap-2"
        :disabled="uploading"
        @click="fileInput?.click()"
      >
        {{ uploading ? 'Uploading…' : form.image_url ? 'Change Image' : 'Upload Image' }}
      </button>
    </div>

    <!-- Categories -->
    <div v-if="sortedCategories.length > 0">
      <h3 class="text-base font-semibold text-gray-900 mb-3">Categories</h3>
      <div class="space-y-3">
        <div v-for="cat in sortedCategories" :key="cat.id">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">
            {{ cat.id.replace('_', ' ') }}
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="item in [...cat.items].sort((a, b) => itemLabel(a.id).localeCompare(itemLabel(b.id)))"
              :key="item.id"
              type="button"
              class="px-3 py-1 rounded-full text-sm border transition-colors"
              :class="form.category_item_ids.includes(item.id)
                ? 'bg-emerald-600 text-white border-emerald-600'
                : 'bg-white text-gray-600 border-gray-300 hover:border-emerald-400'"
              @click="toggleCategoryItem(item.id)"
            >
              {{ itemLabel(item.id) }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tags -->
    <div>
      <h3 class="text-base font-semibold text-gray-900 mb-3">Tags</h3>

      <!-- Selected tags -->
      <div v-if="selectedTags.length > 0" class="flex flex-wrap gap-2 mb-3">
        <span
          v-for="tag in selectedTags"
          :key="tag.id"
          class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-violet-100 text-violet-700"
        >
          {{ tag.name }}
          <button
            type="button"
            class="text-violet-400 hover:text-violet-700 leading-none"
            @click="removeTag(tag.id)"
          >
            ×
          </button>
        </span>
      </div>

      <!-- Typeahead input -->
      <div class="relative">
        <input
          v-model="tagQuery"
          type="text"
          class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          placeholder="Search or add tag…"
          autocomplete="off"
          @focus="tagDropdownOpen = true"
          @blur="scheduleCloseDropdown"
        />
        <div
          v-if="tagDropdownOpen && (filteredSuggestions.length > 0 || showCreateOption)"
          class="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-48 overflow-y-auto"
        >
          <button
            v-for="tag in filteredSuggestions"
            :key="tag.id"
            type="button"
            class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
            @click="selectTag(tag)"
          >
            {{ tag.name }}
          </button>
          <button
            v-if="showCreateOption"
            type="button"
            class="w-full text-left px-3 py-2 text-sm text-violet-600 hover:bg-violet-50 border-t border-gray-100"
            @click="handleCreateTag"
          >
            Create "{{ tagQuery.trim() }}"
          </button>
        </div>
      </div>
      <p v-if="tagError" class="mt-1 text-sm text-red-600">{{ tagError }}</p>
    </div>

    <!-- Ingredients -->
    <div>
      <h3 class="text-base font-semibold text-gray-900 mb-3">Ingredients</h3>
      <div class="space-y-2">
        <div
          v-for="(ing, i) in form.ingredients"
          :key="i"
          class="flex gap-2 items-start"
        >
          <input
            v-model="ing.quantity"
            class="w-20 border border-gray-300 rounded-md px-2 py-1.5 text-sm"
            placeholder="Qty"
          />
          <input
            v-model="ing.unit"
            class="w-20 border border-gray-300 rounded-md px-2 py-1.5 text-sm"
            placeholder="Unit"
          />
          <input
            v-model="ing.name"
            required
            class="flex-1 border border-gray-300 rounded-md px-2 py-1.5 text-sm"
            placeholder="Ingredient name *"
          />
          <input
            v-model="ing.notes"
            class="w-32 border border-gray-300 rounded-md px-2 py-1.5 text-sm"
            placeholder="Notes"
          />
          <button
            type="button"
            class="text-gray-400 hover:text-red-500 mt-1.5 text-lg leading-none"
            @click="removeIngredient(i)"
          >
            ×
          </button>
        </div>
      </div>
      <button
        type="button"
        class="mt-2 text-sm text-emerald-600 hover:underline"
        @click="addIngredient"
      >
        + Add ingredient
      </button>
    </div>

    <!-- Steps -->
    <div>
      <h3 class="text-base font-semibold text-gray-900 mb-3">Steps</h3>
      <div class="space-y-3">
        <div
          v-for="(step, i) in form.steps"
          :key="i"
          class="flex gap-3 items-start"
        >
          <span class="text-emerald-600 font-bold mt-2 shrink-0">{{ step.position }}.</span>
          <textarea
            v-model="step.text"
            required
            rows="2"
            class="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm"
            :placeholder="`Step ${step.position}`"
          />
          <button
            type="button"
            class="text-gray-400 hover:text-red-500 mt-2 text-lg leading-none"
            @click="removeStep(i)"
          >
            ×
          </button>
        </div>
      </div>
      <button
        type="button"
        class="mt-2 text-sm text-emerald-600 hover:underline"
        @click="addStep"
      >
        + Add step
      </button>
    </div>

    <!-- Submit -->
    <div class="pt-4 border-t border-gray-200">
      <button
        type="submit"
        class="bg-emerald-600 text-white px-6 py-2.5 rounded-md text-sm font-medium hover:bg-emerald-700"
      >
        {{ submitLabel ?? 'Save Recipe' }}
      </button>
    </div>
  </form>
</template>
