<script setup>
import { nextTick, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { KIND_LABELS } from '../tickets'

const route = useRoute()
const router = useRouter()
const open = ref(false)
const form = ref(null)
const error = ref('')
const busy = ref(false)
const dialog = ref(null)

async function show() {
  form.value = { kind: 'bug', title: '', description: '', page: route.fullPath }
  error.value = ''
  open.value = true
  await nextTick()
  dialog.value?.querySelector('input[name=title]')?.focus()
}

async function submit() {
  error.value = ''
  busy.value = true
  try {
    const ticket = await api('/tickets', { method: 'POST', body: form.value })
    open.value = false
    router.push(`/meldingen/${ticket.id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <button class="report" type="button" title="Bug of idee melden" @click="show">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 6a4 4 0 0 1 8 0M6 10h12v4a6 6 0 0 1-12 0zM12 10v10M3 9l3 2M21 9l-3 2M3 18l3-2M21 18l-3-2" /></svg>
    <span>Melden</span>
  </button>

  <div v-if="open" class="backdrop" @click.self="open = false" @keydown.esc="open = false">
    <form ref="dialog" class="card dialog" role="dialog" aria-modal="true" aria-labelledby="report-title" @submit.prevent="submit">
      <h2 id="report-title">Iets melden</h2>
      <p class="small muted">Een bug, een idee of een vraag over de site? De admins krijgen het te zien; jij kunt de melding volgen onder <RouterLink to="/meldingen" @click="open = false">Mijn meldingen</RouterLink>.</p>
      <div v-if="error" class="notice error">{{ error }}</div>
      <div class="kinds" role="radiogroup" aria-label="Soort melding">
        <label v-for="(label, kind) in KIND_LABELS" :key="kind" :class="{ on: form.kind === kind }">
          <input v-model="form.kind" type="radio" :value="kind" /> {{ label }}
        </label>
      </div>
      <label class="field"><span>Korte omschrijving</span><input v-model="form.title" name="title" required minlength="3" maxlength="160" placeholder="Bijv. Teller toont verkeerde datum" /></label>
      <label class="field">
        <span>{{ form.kind === 'bug' ? 'Wat ging er mis, en wat had je verwacht?' : 'Toelichting' }}</span>
        <textarea v-model="form.description" rows="5" required maxlength="5000" />
      </label>
      <label class="field">
        <span>Pagina</span>
        <input v-model="form.page" maxlength="300" />
        <small>Automatisch ingevuld met de pagina waar je nu bent.</small>
      </label>
      <div class="row">
        <button class="btn signal" :disabled="busy">Versturen</button>
        <button type="button" class="btn ghost" @click="open = false">Annuleren</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.report {
  position: fixed; right: 16px; bottom: 16px; z-index: 6;
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 14px; border-radius: 999px; border: 1.5px solid var(--line);
  background: var(--surface); color: var(--ink); font: 600 0.85rem var(--sans);
  box-shadow: var(--shadow); cursor: pointer;
}
.report:hover { border-color: var(--signal); }
.report svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; }
.backdrop { position: fixed; inset: 0; z-index: 20; background: rgba(6, 11, 20, 0.6); display: grid; place-items: center; padding: 16px; overflow-y: auto; }
.dialog { width: min(560px, 100%); }
.kinds { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.kinds label { position: relative; border: 1.5px solid var(--line); border-radius: 999px; padding: 6px 14px; cursor: pointer; font-weight: 600; font-size: 0.9rem; }
.kinds label.on { border-color: var(--signal); background: color-mix(in srgb, var(--signal) 18%, transparent); }
.kinds input { position: absolute; inset: 0; margin: 0; opacity: 0; pointer-events: none; }
.kinds label:focus-within { outline: 3px solid var(--signal); }
</style>
