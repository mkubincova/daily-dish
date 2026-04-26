<script setup lang="ts">
import { PhCheck, PhX } from "@phosphor-icons/vue";
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
	if (idx >= 0) form.category_item_ids.splice(idx, 1);
	else form.category_item_ids.push(itemId);
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
	if (!form.tag_ids.includes(tag.id)) form.tag_ids.push(tag.id);
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
  <form class="space-y-8" @submit.prevent="handleSubmit">
    <!-- Basic info -->
    <div class="space-y-4">
      <div>
        <label class="dish-field-label mb-1.5">Title *</label>
        <input
          v-model="form.title"
          required
          class="w-full dish-input"
          placeholder="e.g. Chocolate Chip Cookies"
        />
      </div>

      <div>
        <label class="dish-field-label mb-1.5">Description</label>
        <textarea
          v-model="form.description"
          rows="3"
          class="w-full dish-input resize-none"
        />
      </div>
    </div>

    <!-- Times & servings -->
    <div>
      <p class="dish-section-label mb-3">Details</p>
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="dish-field-label mb-1.5">Servings</label>
          <input
            v-model.number="form.servings"
            type="number"
            min="1"
            class="w-full dish-input"
          />
        </div>
        <div>
          <label class="dish-field-label mb-1.5">Prep (min)</label>
          <input
            v-model.number="form.prep_time_minutes"
            type="number"
            min="0"
            class="w-full dish-input"
          />
        </div>
        <div>
          <label class="dish-field-label mb-1.5">Cook (min)</label>
          <input
            v-model.number="form.cook_time_minutes"
            type="number"
            min="0"
            class="w-full dish-input"
          />
        </div>
      </div>
    </div>

    <!-- Image upload -->
    <div>
      <p class="dish-section-label mb-3">Hero Image</p>
      <img
        v-if="form.image_url"
        :src="form.image_url"
        alt="Recipe hero"
        class="h-40 w-auto max-w-xs object-cover mb-3"
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
        class="dish-btn-secondary px-4 py-2 disabled:opacity-50"
        :disabled="uploading"
        @click="fileInput?.click()"
      >
        {{
          uploading
            ? "Uploading…"
            : form.image_url
              ? "Change Image"
              : "Upload Image"
        }}
      </button>
    </div>

    <!-- Visibility -->
    <div>
      <p class="dish-section-label mb-3">Visibility</p>
      <button
        type="button"
        class="flex items-center gap-2.5 group"
        @click="form.is_public = !form.is_public"
      >
        <span
          class="w-3.5 h-3.5 border shrink-0 flex items-center justify-center transition-colors"
          :class="
            form.is_public
              ? 'bg-dish-fg border-dish-fg'
              : 'border-dish-fg/40 group-hover:border-dish-fg'
          "
        >
          <PhCheck
            v-if="form.is_public"
            class="w-2.5 h-2.5 text-white"
            :weight="'bold'"
          />
        </span>
        <span
          class="font-mono text-xs uppercase tracking-widest text-dish-fg/70"
          >Public (visible to everyone)</span
        >
      </button>
    </div>

    <!-- Source URL -->
    <div>
      <label class="dish-field-label mb-1.5">Source URL</label>
      <input
        v-model="form.source_url"
        type="url"
        class="w-full dish-input"
        placeholder="https://..."
      />
    </div>

    <!-- Categories -->
    <div v-if="sortedCategories.length > 0">
      <p class="dish-section-label mb-3">Categories</p>
      <div class="space-y-4">
        <div v-for="cat in sortedCategories" :key="cat.id">
          <p
            class="font-mono text-[10px] uppercase tracking-widest text-dish-fg/50 mb-2"
          >
            {{ cat.id.replace("_", " ") }}
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="item in [...cat.items].sort((a, b) =>
                itemLabel(a.id).localeCompare(itemLabel(b.id)),
              )"
              :key="item.id"
              type="button"
              class="px-3 py-1 font-mono text-xs uppercase tracking-widest border transition-colors"
              :class="
                form.category_item_ids.includes(item.id)
                  ? 'bg-dish-fg text-dish-surface border-dish-fg'
                  : 'text-dish-fg/60 border-dish-fg/25 hover:border-dish-fg hover:text-dish-fg'
              "
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
      <p class="dish-section-label mb-3">Tags</p>

      <!-- Selected tags -->
      <div v-if="selectedTags.length > 0" class="flex flex-wrap gap-1.5 mb-3">
        <span
          v-for="tag in selectedTags"
          :key="tag.id"
          class="dish-tag inline-flex items-center gap-1"
        >
          {{ tag.name }}
          <button
            type="button"
            class="text-dish-surface/50 hover:text-dish-surface transition-colors leading-none"
            @click="removeTag(tag.id)"
          >
            <PhX class="w-2.5 h-2.5" />
          </button>
        </span>
      </div>

      <!-- Typeahead -->
      <div class="relative">
        <input
          v-model="tagQuery"
          type="text"
          class="w-full dish-input"
          placeholder="Search or add tag…"
          autocomplete="off"
          @focus="tagDropdownOpen = true"
          @blur="scheduleCloseDropdown"
        />
        <div
          v-if="
            tagDropdownOpen &&
            (filteredSuggestions.length > 0 || showCreateOption)
          "
          class="absolute z-10 mt-px w-full bg-dish-surface border border-dish-fg/20 shadow-md max-h-48 overflow-y-auto"
        >
          <button
            v-for="tag in filteredSuggestions"
            :key="tag.id"
            type="button"
            class="w-full text-left px-3 py-2 text-sm text-dish-fg hover:bg-dish-bg transition-colors"
            @click="selectTag(tag)"
          >
            {{ tag.name }}
          </button>
          <button
            v-if="showCreateOption"
            type="button"
            class="w-full text-left px-3 py-2 text-sm text-dish-primary hover:bg-dish-bg transition-colors border-t border-dish-fg/10"
            @click="handleCreateTag"
          >
            Create "{{ tagQuery.trim() }}"
          </button>
        </div>
      </div>
      <p v-if="tagError" class="mt-1 font-mono text-xs text-dish-secondary">
        {{ tagError }}
      </p>
    </div>

    <!-- Ingredients -->
    <div>
      <p class="dish-section-label mb-3">Ingredients</p>
      <div class="space-y-2">
        <div
          v-for="(ing, i) in form.ingredients"
          :key="i"
          class="grid grid-cols-[1fr_1fr] sm:grid-cols-[5rem_5rem_1fr_8rem_auto] gap-2 items-start"
        >
          <input
            v-model="ing.quantity"
            class="dish-input-sm"
            placeholder="Qty"
          />
          <input
            v-model="ing.unit"
            class="dish-input-sm"
            placeholder="Unit"
          />
          <input
            v-model="ing.name"
            required
            class="col-span-2 sm:col-span-1 dish-input-sm"
            placeholder="Ingredient name *"
          />
          <input
            v-model="ing.notes"
            class="dish-input-sm"
            placeholder="Notes"
          />
          <button
            type="button"
            class="text-dish-fg/30 hover:text-dish-secondary transition-colors mt-1.5 justify-self-end sm:justify-self-auto"
            @click="removeIngredient(i)"
          >
            <PhX class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
      <button
        type="button"
        class="mt-3 font-mono text-xs uppercase tracking-widest text-dish-primary hover:text-dish-fg transition-colors"
        @click="addIngredient"
      >
        + Add Ingredient
      </button>
    </div>

    <!-- Steps -->
    <div>
      <p class="dish-section-label mb-3">Steps</p>
      <div class="space-y-3">
        <div
          v-for="(step, i) in form.steps"
          :key="i"
          class="flex gap-3 items-start"
        >
          <span
            class="font-display font-black text-dish-primary text-lg shrink-0 mt-2 w-5"
            >{{ step.position }}.</span
          >
          <textarea
            v-model="step.text"
            required
            rows="2"
            class="flex-1 dish-input resize-none"
            :placeholder="`Step ${step.position}`"
          />
          <button
            type="button"
            class="text-dish-fg/30 hover:text-dish-secondary transition-colors mt-2.5 shrink-0"
            @click="removeStep(i)"
          >
            <PhX class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
      <button
        type="button"
        class="mt-3 font-mono text-xs uppercase tracking-widest text-dish-primary hover:text-dish-fg transition-colors"
        @click="addStep"
      >
        + Add Step
      </button>
    </div>

    <!-- Submit -->
    <div class="pt-4 border-t border-dish-fg/10 flex justify-end">
      <button type="submit" class="dish-btn-primary px-6 py-2.5">
        {{ submitLabel ?? "Save Recipe" }}
      </button>
    </div>
  </form>
</template>
