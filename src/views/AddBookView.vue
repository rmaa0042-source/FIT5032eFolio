<script setup>
import { ref } from 'vue'
import {
  addDoc,
  collection,
  serverTimestamp
} from 'firebase/firestore'
import { db } from '../firebase'
import BookList from '../components/BookList.vue'

const isbn = ref('')
const name = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)
const refreshKey = ref(0)

const addBook = async () => {
  successMessage.value = ''
  errorMessage.value = ''

  const numericIsbn = Number(isbn.value)

  if (!name.value.trim()) {
    errorMessage.value = 'Please enter the book name.'
    return
  }

  if (!Number.isInteger(numericIsbn) || numericIsbn <= 0) {
    errorMessage.value = 'ISBN must be a positive whole number.'
    return
  }

  try {
    isSubmitting.value = true

    await addDoc(collection(db, 'books'), {
      isbn: numericIsbn,
      name: name.value.trim(),
      createdAt: serverTimestamp()
    })

    successMessage.value = 'Book added to Firestore successfully.'

    isbn.value = ''
    name.value = ''

    refreshKey.value += 1
  } catch (error) {
    console.error('Error adding book:', error)
    errorMessage.value = 'Unable to add the book. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="container py-4">
    <section class="add-book-card mx-auto">
      <h1 class="h2 text-center">Add a Book</h1>

      <p class="text-secondary text-center">
        Add a new book record to Cloud Firestore.
      </p>

      <form novalidate @submit.prevent="addBook">
        <div class="mb-3">
          <label for="book-isbn" class="form-label">ISBN</label>

          <input
            id="book-isbn"
            v-model="isbn"
            class="form-control"
            type="number"
            min="1"
            step="1"
            required
          />
        </div>

        <div class="mb-3">
          <label for="book-name" class="form-label">
            Book name
          </label>

          <input
            id="book-name"
            v-model="name"
            class="form-control"
            type="text"
            maxlength="100"
            required
          />
        </div>

        <div
          v-if="successMessage"
          class="alert alert-success"
          role="status"
        >
          {{ successMessage }}
        </div>

        <div
          v-if="errorMessage"
          class="alert alert-danger"
          role="alert"
        >
          {{ errorMessage }}
        </div>

        <button
          class="btn btn-primary w-100"
          type="submit"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? 'Adding book...' : 'Add Book' }}
        </button>
      </form>
    </section>

    <BookList :key="refreshKey" />
  </main>
</template>

<style scoped>
.add-book-card {
  max-width: 520px;
  padding: 2rem;
  background: #ffffff;
  border: 1px solid #dee2e6;
  border-radius: 1rem;
  box-shadow: 0 1rem 2.5rem rgba(23, 59, 105, 0.1);
}
</style>