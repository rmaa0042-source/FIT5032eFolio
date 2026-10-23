<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'

const jsonData = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const getAllBooks = async () => {
  const endpoint = import.meta.env.VITE_GET_ALL_BOOKS_FUNCTION_URL

  if (!endpoint) {
    errorMessage.value =
      'Add VITE_GET_ALL_BOOKS_FUNCTION_URL to .env after deploying getAllBooksAPI.'
    isLoading.value = false
    return
  }

  try {
    const response = await axios.get(endpoint)
    jsonData.value = response.data
  } catch (error) {
    console.error('Unable to load books API:', error)
    errorMessage.value = 'Unable to load JSON data from the books API.'
  } finally {
    isLoading.value = false
  }
}

onMounted(getAllBooks)
</script>

<template>
  <main class="container py-5">
    <h1>Get All Book API</h1>
    <p class="text-secondary">
      JSON returned by the deployed Firebase Cloud Function.
    </p>

    <p v-if="isLoading">Loading...</p>
    <p v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </p>
    <pre v-if="jsonData" class="json-output">{{ JSON.stringify(jsonData, null, 2) }}</pre>
  </main>
</template>

<style scoped>
.json-output {
  padding: 1.5rem;
  overflow-x: auto;
  color: #f8f9fa;
  background: #212529;
  border-radius: 0.75rem;
}
</style>
