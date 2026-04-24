<script setup lang="ts">
interface Ingredient {
  position: number
  quantity: string
  unit: string
  name: string
  notes: string
}

interface Step {
  position: number
  text: string
}

interface RecipeFormData {
  title: string
  description: string
  servings: number | null
  prep_time_minutes: number | null
  cook_time_minutes: number | null
  source_url: string
  is_public: boolean
  image_url: string
  image_public_id: string
  ingredients: Ingredient[]
  steps: Step[]
}

const props = defineProps<{
  initial?: Partial<RecipeFormData>
  submitLabel?: string
}>()

const emit = defineEmits<{
  submit: [data: RecipeFormData]
}>()

const config = useRuntimeConfig()

const form = reactive<RecipeFormData>({
  title: props.initial?.title ?? '',
  description: props.initial?.description ?? '',
  servings: props.initial?.servings ?? null,
  prep_time_minutes: props.initial?.prep_time_minutes ?? null,
  cook_time_minutes: props.initial?.cook_time_minutes ?? null,
  source_url: props.initial?.source_url ?? '',
  is_public: props.initial?.is_public ?? true,
  image_url: props.initial?.image_url ?? '',
  image_public_id: props.initial?.image_public_id ?? '',
  ingredients: props.initial?.ingredients?.map((i: any) => ({
    position: i.position,
    quantity: String(i.quantity ?? ''),
    unit: i.unit ?? '',
    name: i.name,
    notes: i.notes ?? '',
  })) ?? [{ position: 1, quantity: '', unit: '', name: '', notes: '' }],
  steps: props.initial?.steps?.map((s: any) => ({
    position: s.position,
    text: s.text,
  })) ?? [{ position: 1, text: '' }],
})

function addIngredient() {
  form.ingredients.push({
    position: form.ingredients.length + 1,
    quantity: '',
    unit: '',
    name: '',
    notes: '',
  })
}

function removeIngredient(index: number) {
  form.ingredients.splice(index, 1)
  form.ingredients.forEach((ing, i) => { ing.position = i + 1 })
}

function addStep() {
  form.steps.push({ position: form.steps.length + 1, text: '' })
}

function removeStep(index: number) {
  form.steps.splice(index, 1)
  form.steps.forEach((s, i) => { s.position = i + 1 })
}

// Cloudinary upload
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

async function uploadImage(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const params = await $fetch<{
      cloud_name: string
      api_key: string
      timestamp: number
      signature: string
      folder: string
    }>(`${config.public.apiUrl}/uploads/sign`, {
      method: 'POST',
      credentials: 'include',
    })
    const fd = new FormData()
    fd.append('file', file)
    fd.append('api_key', params.api_key)
    fd.append('timestamp', String(params.timestamp))
    fd.append('signature', params.signature)
    fd.append('folder', params.folder)

    const res = await fetch(
      `https://api.cloudinary.com/v1_1/${params.cloud_name}/image/upload`,
      { method: 'POST', body: fd }
    )
    const data = await res.json()
    form.image_url = data.secure_url
    form.image_public_id = data.public_id
  } finally {
    uploading.value = false
  }
}

function handleSubmit() {
  const data = {
    ...form,
    ingredients: form.ingredients.map(ing => ({
      ...ing,
      quantity: ing.quantity === '' ? null : ing.quantity,
      unit: ing.unit === '' ? null : ing.unit,
      notes: ing.notes === '' ? null : ing.notes,
    })),
  }
  emit('submit', data as any)
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
