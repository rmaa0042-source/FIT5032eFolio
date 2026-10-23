<script setup>
import { currentUser } from '../services/auth'
</script>

<template>
  <main class="container py-4">
    <h1>About Our Library</h1>

    <p>
      Welcome to our digital library! We are dedicated to providing
      books and resources to our community.
    </p>

    <div class="alert alert-success" role="status">
      Welcome,
      <strong>{{ currentUser?.email }}</strong>!
      Your role is
      <strong>{{ currentUser?.displayName || 'Member' }}</strong>.
      You are viewing members-only content.
    </div>
  </main>
</template>