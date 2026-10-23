<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const requestedRoute = computed(() =>
  typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
    ? route.query.redirect
    : '/about'
)
</script>

<template>
  <section class="denied-card mx-auto text-center" aria-labelledby="denied-title">
    <div class="lock-icon" aria-hidden="true">🔒</div>
    <p class="text-uppercase fw-semibold text-danger mb-2">Route guard activated</p>
    <h1 id="denied-title">Access Denied</h1>
    <p class="lead text-secondary">
      The requested route <code>{{ requestedRoute }}</code> is restricted to authenticated members.
    </p>
    <RouterLink
      class="btn btn-primary me-2"
      :to="{ name: 'Login', query: { redirect: requestedRoute } }"
    >
      Login to continue
    </RouterLink>
    <RouterLink class="btn btn-outline-secondary" to="/">Return Home</RouterLink>
  </section>
</template>

<style scoped>
.denied-card {
  max-width: 680px;
  padding: 3rem;
  background: #fff;
  border: 1px solid #fecaca;
  border-radius: 1rem;
  box-shadow: 0 1rem 2.5rem rgba(127, 29, 29, 0.1);
}

.lock-icon {
  font-size: 3rem;
}
</style>
