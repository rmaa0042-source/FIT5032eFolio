import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig({
  // GitHub Pages serves project sites from /<repository-name>/, while
  // Cloudflare Pages serves this project from the domain root.
  base: process.env.GITHUB_ACTIONS
    ? `/${process.env.GITHUB_REPOSITORY?.split('/')[1] ?? ''}/`
    : '/',
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
