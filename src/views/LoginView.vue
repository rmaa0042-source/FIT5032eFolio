<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { login } from '../services/auth'

const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const loginError = ref('')
const isLoading = ref(false)

const safeRedirect = () => {
  const requested =
    typeof route.query.redirect === 'string'
      ? route.query.redirect
      : '/about'

  return requested.startsWith('/') && !requested.startsWith('//')
    ? requested
    : '/about'
}

const submitLogin = async () => {
  loginError.value = ''
  isLoading.value = true

  try {
    await login(email.value.trim(), password.value)
    await router.replace(safeRedirect())
  } catch (error) {
    console.error('Login error:', error.code)

    if (
      error.code === 'auth/invalid-credential' ||
      error.code === 'auth/user-not-found' ||
      error.code === 'auth/wrong-password'
    ) {
      loginError.value = 'Invalid email or password.'
    } else {
      loginError.value = 'Unable to log in. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <section class="login-card mx-auto" aria-labelledby="login-title">
    <h1 id="login-title" class="h2 text-center">Member Login</h1>

    <p class="text-secondary text-center">
      Sign in with your registered Firebase account.
    </p>

    <div
      v-if="route.query.denied === 'true'"
      class="alert alert-warning"
      role="alert"
    >
      Access denied. Please log in before opening the protected page.
    </div>

    <form novalidate @submit.prevent="submitLogin">
      <div class="mb-3">
        <label class="form-label" for="login-email">Email</label>
        <input
          id="login-email"
          v-model="email"
          class="form-control"
          type="email"
          autocomplete="email"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label" for="login-password">Password</label>
        <input
          id="login-password"
          v-model="password"
          class="form-control"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>

      <div
        v-if="loginError"
        class="alert alert-danger"
        role="alert"
      >
        {{ loginError }}
      </div>

      <button
        class="btn btn-primary w-100"
        type="submit"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>

    <p class="text-center mt-3 mb-0">
      Do not have an account?
      <router-link to="/register">Register here</router-link>
    </p>
  </section>
</template>

<style scoped>
.login-card {
  max-width: 480px;
  padding: 2rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 1rem;
  box-shadow: 0 1rem 2.5rem rgba(23, 59, 105, 0.1);
}
</style>