import { createRouter, createWebHashHistory } from 'vue-router'
import { isAuthenticated } from '../services/auth'
import { auth } from '../firebase'

import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AccessDeniedView from '../views/AccessDeniedView.vue'
import AddBookView from '../views/AddBookView.vue'
import GetBookCountView from '../views/GetBookCountView.vue'
import WeatherView from '../views/WeatherView.vue'
import GetAllBookAPIView from '../views/GetAllBookAPIView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/add-book',
    name: 'AddBook',
    component: AddBookView,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/get-book-count',
    name: 'GetBookCount',
    component: GetBookCountView
  },
  {
    path: '/weather-check',
    name: 'GetWeather',
    component: WeatherView
  },
  {
    path: '/get-all-book-api',
    name: 'GetAllBookAPI',
    component: GetAllBookAPIView
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      guestOnly: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: {
      guestOnly: true
    }
  },
  {
    path: '/access-denied',
    name: 'AccessDenied',
    component: AccessDeniedView
  }
]

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to) => {
  await auth.authStateReady()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return {
      name: 'Login',
      query: {
        redirect: to.fullPath,
        denied: 'true'
      }
    }
  }

  if (to.meta.guestOnly && isAuthenticated.value) {
    return {
      name: 'About'
    }
  }

  return true
})

export default router
