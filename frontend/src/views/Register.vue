<script setup>
import { ref } from 'vue'
import { api } from '../api'

const form = ref({ name: '', email: '', password: '' })
const agreed = ref(false)
const error = ref('')
const done = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    const res = await api('/auth/register', { method: 'POST', body: form.value })
    done.value = res.message
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="auth page">
    <div v-if="done" class="card">
      <span class="eyebrow">Ingecheckt</span>
      <h1>Bijna binnen</h1>
      <p>{{ done }}</p>
      <p class="muted small">Laat het even weten in de groepsapp, dan gaat het sneller.</p>
      <RouterLink to="/" class="btn ghost">Terug naar home</RouterLink>
    </div>

    <form v-else class="card" @submit.prevent="submit">
      <span class="eyebrow">Word Trauma Tram Teller</span>
      <h1>Aanmelden</h1>
      <p class="muted small">Na het aanmelden keurt een admin je account goed. Daarna kun je inloggen.</p>
      <div v-if="error" class="notice error">{{ error }}</div>
      <label class="field"><span>Naam</span><input v-model="form.name" autocomplete="name" required minlength="2" maxlength="80" /></label>
      <label class="field"><span>E-mailadres</span><input v-model="form.email" type="email" autocomplete="email" required /></label>
      <label class="field">
        <span>Wachtwoord</span>
        <input v-model="form.password" type="password" autocomplete="new-password" required minlength="10" />
        <small>Minimaal 10 tekens.</small>
      </label>
      <label class="row consent small">
        <input v-model="agreed" type="checkbox" required />
        <span>Ik heb het <RouterLink to="/privacy" target="_blank">privacybeleid</RouterLink> gelezen.</span>
      </label>
      <button class="btn signal full" :disabled="busy || !agreed">Account aanvragen</button>
      <p class="small muted alt">Al een account? <RouterLink to="/inloggen">Log in</RouterLink></p>
    </form>
  </div>
</template>

<style scoped>
.auth { width: min(440px, 100% - 32px); margin-inline: auto; }
.consent { flex-wrap: nowrap; align-items: flex-start; margin-bottom: 16px; }
.consent input { margin-top: 4px; }
.full { width: 100%; }
.alt { margin: 16px 0 0; text-align: center; }
</style>
