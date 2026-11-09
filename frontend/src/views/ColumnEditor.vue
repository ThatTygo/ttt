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
  }
})

async function save() {
  error.value = ''
  saving.value = true
  try {
    const body = { ...form.value, published_at: form.value.published_at || null }
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

      <div class="row">
        <button class="btn signal" :disabled="saving">{{ isNew ? 'Publiceren' : 'Opslaan' }}</button>
        <RouterLink :to="isNew ? '/columns' : `/columns/${id}`" class="btn ghost">Annuleren</RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped>
.label { font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); }
.tabs { display: flex; gap: 4px; background: var(--paper); border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
.tabs button { border: 0; background: none; color: var(--muted); font: 600 0.8rem var(--sans); padding: 4px 12px; border-radius: 999px; cursor: pointer; }
.tabs button.on { background: var(--ink); color: var(--paper); }
textarea { font-family: var(--serif); font-size: 1.05rem; line-height: 1.6; }
.preview { min-height: 320px; padding: 16px; border: 1.5px dashed var(--line); border-radius: 10px; font-size: 1.05rem; }
</style>
