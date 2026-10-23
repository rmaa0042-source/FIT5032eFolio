<script setup>
import { ref } from 'vue'
import axios from 'axios'

const count = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const getBookCount = async () => {
  const endpoint = import.meta.env.VITE_COUNT_BOOKS_FUNCTION_URL

  count.value = null
  errorMessage.value = ''

  if (!endpoint) {
    errorMessage.value =
      'Add VITE_COUNT_BOOKS_FUNCTION_URL to .env after deploying countBooks.'
    return
  }

  try {
    isLoading.value = true
    const response = await axios.get(endpoint)
    count.value = Number(response.data.count)
  } catch (error) {
    console.error('Unable to obtain the book count:', error)
    errorMessage.value = 'Unable to obtain the book count. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="container py-5 text-center">
    <h1 class="mb-4">Book Counter</h1>

    <button
      class="btn btn-primary"
      type="button"
      :disabled="isLoading"
      @click="getBookCount"
    >
      {{ isLoading ? 'Loading...' : 'Get Book Count' }}
    </button>

    <p v-if="count !== null" class="fs-4 mt-4" role="status">
      Total number of books: <strong>{{ count }}</strong>
    </p>

    <p v-if="errorMessage" class="alert alert-danger mt-4" role="alert">
      {{ errorMessage }}
    </p>
  </main>
</template>
