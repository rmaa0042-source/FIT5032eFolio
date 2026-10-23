<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

const apiKey = import.meta.env.VITE_OPENWEATHER_API_KEY
const city = ref('Clayton')
const weatherData = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const temperature = computed(() =>
  weatherData.value ? Math.round(weatherData.value.main.temp - 273.15) : null
)

const iconUrl = computed(() =>
  weatherData.value
    ? `https://openweathermap.org/img/wn/${weatherData.value.weather[0].icon}@2x.png`
    : ''
)

const requestWeather = async (params) => {
  errorMessage.value = ''

  if (!apiKey) {
    errorMessage.value =
      'Add VITE_OPENWEATHER_API_KEY to .env before requesting live weather.'
    return
  }

  try {
    isLoading.value = true
    const response = await axios.get(
      'https://api.openweathermap.org/data/2.5/weather',
      { params: { ...params, appid: apiKey } }
    )
    weatherData.value = response.data
  } catch (error) {
    console.error('Unable to retrieve weather:', error)
    errorMessage.value = 'Weather could not be retrieved for this location.'
  } finally {
    isLoading.value = false
  }
}

const searchByCity = () => {
  const query = city.value.trim()
  if (!query) {
    errorMessage.value = 'Please enter a city name.'
    return
  }
  requestWeather({ q: query })
}

const searchCurrentLocation = () => {
  if (!navigator.geolocation) {
    errorMessage.value = 'Geolocation is not supported by this browser.'
    return
  }

  navigator.geolocation.getCurrentPosition(
    ({ coords }) =>
      requestWeather({ lat: coords.latitude, lon: coords.longitude }),
    () => {
      errorMessage.value =
        'Location permission was not granted. Search by city instead.'
    }
  )
}

onMounted(searchCurrentLocation)
</script>

<template>
  <main class="container py-5">
    <section class="weather-card mx-auto text-center">
      <h1>Weather App</h1>

      <form class="input-group my-4" @submit.prevent="searchByCity">
        <label class="visually-hidden" for="weather-city">City</label>
        <input
          id="weather-city"
          v-model="city"
          class="form-control"
          type="text"
          placeholder="Enter city name"
        />
        <button class="btn btn-primary" type="submit" :disabled="isLoading">
          Search
        </button>
      </form>

      <button
        class="btn btn-outline-secondary btn-sm"
        type="button"
        :disabled="isLoading"
        @click="searchCurrentLocation"
      >
        Use current location
      </button>

      <div v-if="weatherData" class="mt-4" aria-live="polite">
        <h2>{{ weatherData.name }}, {{ weatherData.sys.country }}</h2>
        <img :src="iconUrl" alt="Current weather icon" width="100" height="100" />
        <p class="display-6 mb-1">{{ temperature }} C</p>
        <p class="text-capitalize">{{ weatherData.weather[0].description }}</p>
      </div>

      <p v-if="isLoading" class="mt-4">Loading weather...</p>
      <p v-if="errorMessage" class="alert alert-danger mt-4" role="alert">
        {{ errorMessage }}
      </p>
    </section>
  </main>
</template>

<style scoped>
.weather-card {
  max-width: 560px;
  padding: 2rem;
  border: 1px solid #dee2e6;
  border-radius: 1rem;
  background: #fff;
}
</style>
