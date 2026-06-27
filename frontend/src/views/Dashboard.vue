<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Dashboard</h1>
        <button @click="logout" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm transition duration-200">
          Logout
        </button>
      </div>
      
      <div v-if="token">
        <p class="text-green-600 font-semibold mb-4">Successfully Authenticated!</p>
        <p class="text-gray-600 mb-2">Your JSON Web Token (JWT):</p>
        <div class="bg-gray-100 p-4 rounded break-all border border-gray-200">
          <code class="text-xs text-gray-700">{{ token }}</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const token = ref(localStorage.getItem('auth_token') || '')

onMounted(() => {
  // 1. Check if the backend passed a token in the URL query string
  const urlToken = route.query.token
  
  if (urlToken) {
    // 2. Save it to state and localStorage
    token.value = urlToken
    localStorage.setItem('auth_token', urlToken)
    
    // 3. Clean up the URL so the token isn't visible in the address bar
    router.replace({ path: '/dashboard' })
  } else if (!token.value) {
    // 4. If there's no token in the URL and no token in storage, kick them out
    router.push('/')
  }
})

const logout = () => {
  localStorage.removeItem('auth_token')
  token.value = ''
  router.push('/')
}
</script>
