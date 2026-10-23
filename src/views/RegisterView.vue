<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../services/auth'

const router = useRouter()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('Member')
const registerError = ref('')
const isLoading = ref(false)

const submitRegistration = async () => {
  registerError.value = ''

  if (password.value !== confirmPassword.value) {
    registerError.value = 'Passwords do not match.'
    return
  }

  if (password.value.length < 6) {
    registerError.value = 'Password must contain at least 6 characters.'
    return
  }

  isLoading.value = true

  try {
    await register(
      email.value.trim(),
      password.value,
      role.value
    )

    await router.push('/about')
  } catch (error) {
    console.error('Registration error:', error.code)

    if (error.code === 'auth/email-already-in-use') {
      registerError.value = 'This email address is already registered.'
    } else if (error.code === 'auth/invalid-email') {
      registerError.value = 'Please enter a valid email address.'
    } else if (error.code === 'auth/weak-password') {
      registerError.value = 'The password is too weak.'
    } else {
      registerError.value = 'Registration failed. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <section class="register-card mx-auto" aria-labelledby="register-title">
    <h1 id="register-title" class="h2 text-center">
      Create an Account
    </h1>

    <p class="text-secondary text-center">
      Register with Firebase to access the library.
    </p>

    <form novalidate @submit.prevent="submitRegistration">
      <div class="mb-3">
        <label class="form-label" for="register-email">Email</label>
        <input
          id="register-email"
          v-model="email"
          class="form-control"
          type="email"
          autocomplete="email"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label" for="register-password">
          Password
        </label>
        <input
          id="register-password"
          v-model="password"
          class="form-control"
          type="password"
          autocomplete="new-password"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label" for="confirm-password">
          Confirm password
        </label>
        <input
          id="confirm-password"
          v-model="confirmPassword"
          class="form-control"
          type="password"
          autocomplete="new-password"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label" for="register-role">Role</label>
        <select
          id="register-role"
          v-model="role"
          class="form-select"
          required
        >
          <option value="Member">Member</option>
          <option value="Librarian">Librarian</option>
        </select>
      </div>

      <div
        v-if="registerError"
        class="alert alert-danger"
        role="alert"
      >
        {{ registerError }}
      </div>

      <button
        class="btn btn-primary w-100"
        type="submit"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Creating account...' : 'Register' }}
      </button>
    </form>

    <p class="text-center mt-3 mb-0">
      Already registered?
      <router-link to="/login">Login here</router-link>
    </p>
  </section>
</template>

<style scoped>
.register-card {
  max-width: 520px;
  padding: 2rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 1rem;
  box-shadow: 0 1rem 2.5rem rgba(23, 59, 105, 0.1);
}
</style>