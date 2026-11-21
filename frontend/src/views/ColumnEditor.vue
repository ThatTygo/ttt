<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../auth'
import { paragraphs, toLocalInput } from '../format'

const props = defineProps({ id: String })
const router = useRouter()

const form = ref({ title: '', author_name: auth.user.name, published_at: toLocalInput(), body: '' })
const authors = ref([])
const error = ref('')
const saving = ref(false)
const preview = ref(false)
const alreadyIncident = ref(false)
const incident = ref({ on: false, day: '', text: '' })

const isNew = computed(() => !props.id)
const previewBody = computed(() => paragraphs(form.value.body))

onMounted(async () => {
  // De ledenlijst is alleen voor admins; editors krijgen alleen bestaande auteurs als suggestie.
  const [list, members] = await Promise.all([
    api('/columns?limit=1'),
    auth.can('admin') ? api('/members') : Promise.resolve([]),
  ])
  authors.value = [...new Set([...members.map((m) => m.name), ...list.authors])].sort()
  if (props.id) {
    const c = await api(`/columns/${props.id}`)
    form.value = { title: c.title, author_name: c.author_name, published_at: toLocalInput(c.published_at), body: c.body }
    alreadyIncident.value = c.has_incident
  }
})

async function save() {
  error.value = ''
  saving.value = true
  try {
    const body = { ...form.value, published_at: form.value.published_at || null }
    if (incident.value.on && !alreadyIncident.value) {
      body.incident = { day: incident.value.day || null, text: incident.value.text || null }
    }
    const saved = isNew.value
      ? await api('/columns', { method: 'POST', body })
      : await api(`/columns/${props.id}`, { method: 'PUT', body })
    router.push(`/columns/${saved.id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="narrow page">
    <span class="eyebrow">{{ isNew ? 'Dagdienst afsluiten' : 'Column bewerken' }}</span>
    <h1>{{ isNew ? 'Nieuwe column' : 'Bewerken' }}</h1>

    <form class="card" @submit.prevent="save">
      <div v-if="error" class="notice error">{{ error }}</div>

      <label class="field">
        <span>Titel</span>
        <input v-model="form.title" required maxlength="160" placeholder="Bijv. De stilte is tijdelijk" />
      </label>

      <div class="grid-2">
        <label class="field">
          <span>Teller (auteur)</span>
          <input v-model="form.author_name" list="authors" required maxlength="120" />
          <datalist id="authors"><option v-for="a in authors" :key="a" :value="a" /></datalist>
        </label>
        <label class="field">
          <span>Datum en tijd</span>
          <input v-model="form.published_at" type="datetime-local" />
        </label>
      </div>

      <div class="field">
        <div class="row spread">
          <span class="label">Tekst</span>
          <div class="tabs" role="tablist">
            <button type="button" :class="{ on: !preview }" @click="preview = false">Schrijven</button>
            <button type="button" :class="{ on: preview }" @click="preview = true">Voorbeeld</button>
          </div>
        </div>
        <textarea
          v-show="!preview"
          v-model="form.body"
          rows="16"
          required
          placeholder="Geachte TTT'ers,&#10;&#10;Mijn dagdienst nadert zijn laatste halte…"
        />
        <div v-show="preview" class="preview prose">
          <p v-for="(p, i) in previewBody" :key="i">{{ p }}</p>
          <p v-if="!previewBody.length" class="muted">Nog niks geschreven. De teller staat ook op nul.</p>
        </div>
        <small>Laat een witregel tussen alinea's.</small>
      </div>

      <div v-if="alreadyIncident" class="incident done">
        Bij deze column is al een sticker geplakt en is de teller bijgewerkt.
      </div>
      <div v-else class="incident" :class="{ on: incident.on }">
        <label class="row check">
          <input v-model="incident.on" type="checkbox" />
          <span><strong>Er was een stickerwaardig tramincident</strong></span>
        </label>
        <template v-if="incident.on">
          <p class="small muted">
            Bij opslaan komt er een sticker bij en springt de teller "dagen sinds het laatste incident" naar deze datum.
            Eerst de artikellink gedeeld in de groep?
          </p>
          <div class="grid-2">
            <label class="field">
              <span>Datum van het incident</span>
              <input v-model="incident.day" type="date" />
              <small>Leeg = datum van deze column.</small>
            </label>
            <label class="field">
              <span>Korte omschrijving</span>
              <input v-model="incident.text" maxlength="300" placeholder="Bijv. Tram ontspoord op de Van Baerlestraat" />
              <small>Leeg = titel van de column.</small>
            </label>
          </div>
        </template>
      </div>

      <div class="row">
        <button class="btn signal" :disabled="saving">{{ isNew ? 'Publiceren' : 'Opslaan' }}</button>
        <RouterLink :to="isNew ? '/columns' : `/columns/${id}`" class="btn ghost">Annuleren</RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped>
.incident { border: 1.5px dashed var(--line); border-radius: 12px; padding: 14px 16px; margin-bottom: 18px; }
.incident.on { border-style: solid; border-color: var(--alarm); }
.incident.done { color: var(--muted); font-size: 0.9rem; }
.incident .check { flex-wrap: nowrap; }
.incident .field { margin-bottom: 0; }
.label { font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); }
.tabs { display: flex; gap: 4px; background: var(--paper); border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
.tabs button { border: 0; background: none; color: var(--muted); font: 600 0.8rem var(--sans); padding: 4px 12px; border-radius: 999px; cursor: pointer; }
.tabs button.on { background: var(--ink); color: var(--paper); }
textarea { font-family: var(--serif); font-size: 1.05rem; line-height: 1.6; }
.preview { min-height: 320px; padding: 16px; border: 1.5px dashed var(--line); border-radius: 10px; font-size: 1.05rem; }
</style>
