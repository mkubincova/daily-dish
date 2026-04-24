<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const config = useRuntimeConfig()

const { data: recipe, error: fetchError } = await useFetch(
  `${config.public.apiUrl}/recipes/${route.params.slug}`,
  { credentials: 'include' as RequestCredentials }
)

if (fetchError.value) {
  throw createError({ statusCode: 404, statusMessage: 'Recipe not found' })
}

const error = ref('')

async function handleSubmit(data: any) {
  error.value = ''
  try {
    await $fetch(`${config.public.apiUrl}/recipes/${(recipe.value as any).id}`, {
      method: 'PATCH',
      credentials: 'include',
      body: {
        ...data,
        servings: data.servings || null,
        prep_time_minutes: data.prep_time_minutes || null,
        cook_time_minutes: data.cook_time_minutes || null,
        source_url: data.source_url || null,
        image_url: data.image_url || null,
        image_public_id: data.image_public_id || null,
      },
    })
    await navigateTo(`/r/${(recipe.value as any).slug}`)
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Failed to save recipe.'
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Edit Recipe</h1>
    <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>
    <RecipeForm
      v-if="recipe"
      :initial="recipe as any"
      submit-label="Save Changes"
      @submit="handleSubmit"
    />
  </div>
</template>
