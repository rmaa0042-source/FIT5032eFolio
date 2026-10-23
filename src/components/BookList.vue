<script setup>
import { onMounted, ref } from 'vue'
import {
  collection,
  deleteDoc,
  doc,
  getDocs,
  limit,
  orderBy,
  query,
  updateDoc,
  where
} from 'firebase/firestore'
import { db } from '../firebase'

const books = ref([])
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const loadBooks = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const booksQuery = query(
      collection(db, 'books'),
      where('isbn', '>', 1000),
      orderBy('isbn', 'asc'),
      limit(5)
    )

    const querySnapshot = await getDocs(booksQuery)

    books.value = querySnapshot.docs.map((bookDocument) => {
      const bookData = bookDocument.data()

      return {
        id: bookDocument.id,
        name: bookData.name,
        isbn: bookData.isbn,
        editName: bookData.name,
        editIsbn: bookData.isbn
      }
    })
  } catch (error) {
    console.error('Error retrieving books:', error)
    errorMessage.value = 'Unable to retrieve books from Firestore.'
  } finally {
    isLoading.value = false
  }
}

const updateBook = async (book) => {
  successMessage.value = ''
  errorMessage.value = ''

  const numericIsbn = Number(book.editIsbn)

  if (!book.editName.trim()) {
    errorMessage.value = 'Book name is required.'
    return
  }

  if (!Number.isInteger(numericIsbn) || numericIsbn <= 0) {
    errorMessage.value = 'ISBN must be a positive whole number.'
    return
  }

  try {
    await updateDoc(doc(db, 'books', book.id), {
      name: book.editName.trim(),
      isbn: numericIsbn
    })

    successMessage.value = 'Book updated successfully.'
    await loadBooks()
  } catch (error) {
    console.error('Error updating book:', error)
    errorMessage.value = 'Unable to update the book.'
  }
}

const deleteBook = async (book) => {
  successMessage.value = ''
  errorMessage.value = ''

  const shouldDelete = window.confirm(
    `Delete "${book.name}" from Firestore?`
  )

  if (!shouldDelete) {
    return
  }

  try {
    await deleteDoc(doc(db, 'books', book.id))
    successMessage.value = 'Book deleted successfully.'
    await loadBooks()
  } catch (error) {
    console.error('Error deleting book:', error)
    errorMessage.value = 'Unable to delete the book.'
  }
}

onMounted(loadBooks)
</script>

<template>
  <section class="book-list mt-5">
    <h2 class="h3">Firestore Query Results</h2>

    <p class="text-secondary">
      Showing a maximum of five books with ISBN greater than 1000,
      ordered by ISBN.
    </p>

    <div class="query-summary mb-3">
      <code>where('isbn', '&gt;', 1000)</code>
      <code>orderBy('isbn', 'asc')</code>
      <code>limit(5)</code>
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

    <p v-if="isLoading">Loading books...</p>

    <p v-else-if="books.length === 0" class="alert alert-info">
      No books matched the Firestore query.
    </p>

    <div v-else class="table-responsive">
      <table class="table table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">Book name</th>
            <th scope="col">ISBN</th>
            <th scope="col">Update</th>
            <th scope="col">Delete</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="book in books" :key="book.id">
            <td>
              <input
                v-model="book.editName"
                class="form-control"
                type="text"
                aria-label="Book name"
              />
            </td>

            <td>
              <input
                v-model="book.editIsbn"
                class="form-control"
                type="number"
                min="1"
                step="1"
                aria-label="ISBN"
              />
            </td>

            <td>
              <button
                class="btn btn-warning btn-sm"
                type="button"
                @click="updateBook(book)"
              >
                Update
              </button>
            </td>

            <td>
              <button
                class="btn btn-danger btn-sm"
                type="button"
                @click="deleteBook(book)"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.book-list {
  max-width: 900px;
  margin-right: auto;
  margin-left: auto;
}

.query-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.query-summary code {
  padding: 0.5rem 0.75rem;
  color: #1f2937;
  background: #f1f5f9;
  border: 1px solid #dbe3ec;
  border-radius: 0.4rem;
}
</style>