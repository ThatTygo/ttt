<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth } from '../auth'

const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    await auth.login(email.value, password.value)
    const back = route.query.terug
    router.push(typeof back === 'string' && back.startsWith('/') && !back.startsWith('//') ? back : '/')
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth page">
    <form class="card" @submit.prevent="submit">
      <span class="eyebrow">Instappen</span>
      <h1>Inloggen</h1>
      <div v-if="error" class="notice error">{{ error }}</div>
      <label class="field"><span>E-mailadres</span><input v-model="email" type="email" autocomplete="email" required /></label>
      <label class="field"><span>Wachtwoord</span><input v-model="password" type="password" autocomplete="current-password" required /></label>
      <button class="btn signal full" :disabled="busy">Inloggen</button>
      <p class="small muted alt">Nog geen account? <RouterLink to="/aanmelden">Meld je aan</RouterLink></p>
    </form>
  </div>
</template>

<style scoped>
.auth { width: min(440px, 100% - 32px); margin-inline: auto; }
.full { width: 100%; margin-top: 4px; }
.alt { margin: 16px 0 0; text-align: center; }
</style>
