<script setup>
import { useRouter } from 'vue-router'
import {
  currentUser,
  isAuthenticated,
  logout
} from '../services/auth'

const router = useRouter()

const handleLogout = async () => {
  await logout()
  await router.push({ name: 'Login' })
}
</script>

<template>
  <header>
    <nav
      class="nav nav-pills justify-content-center align-items-center gap-2 border-bottom pb-3 mb-4"
    >
      <router-link
        to="/"
        class="nav-link"
        active-class="active"
        exact-active-class="active"
      >
        Home (Week 5)
      </router-link>

      <router-link
        to="/about"
        class="nav-link"
        active-class="active"
      >
        About
        <span v-if="!isAuthenticated">🔒</span>
      </router-link>

      <router-link to="/get-book-count" class="nav-link" active-class="active">
        Get Book Count
      </router-link>

      <router-link to="/weather-check" class="nav-link" active-class="active">
        Get Weather
      </router-link>

      <router-link to="/get-all-book-api" class="nav-link" active-class="active">
        Get All Book API
      </router-link>

      <template v-if="isAuthenticated">
        <router-link
          to="/add-book"
          class="nav-link"
          active-class="active"
        >
          Add Book
        </router-link>

        <span class="nav-link text-dark">
          {{ currentUser?.email }}
          ({{ currentUser?.displayName || 'Member' }})
        </span>

        <button
          class="btn btn-outline-primary btn-sm"
          type="button"
          @click="handleLogout"
        >
          Logout
        </button>
      </template>

      <template v-else>
        <router-link
          to="/login"
          class="nav-link"
          active-class="active"
        >
          Login
        </router-link>

        <router-link
          to="/register"
          class="nav-link"
          active-class="active"
        >
          Register
        </router-link>
      </template>
    </nav>
  </header>
</template>
