<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BHeader from './components/BHeader.vue'

const route = useRoute()
const showHeader = computed(() => route.name !== 'GetAllBookAPI')
</script>

<template>
  <div class="main-container">
    <header v-if="showHeader">
      <BHeader />
    </header>

    <main class="main-box">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.main-container {
  min-height: 100vh;
}

.main-box {
  padding-bottom: 3rem;
}
</style>
