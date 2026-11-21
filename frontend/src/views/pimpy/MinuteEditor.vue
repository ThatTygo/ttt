<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api'
import { amsterdamDay, formatDate } from '../../format'
import { SYNTAX_HELP } from '../../pimpy'

const router = useRouter()
const groups = ref([])
const form = ref({ group_id: '', minute_date: amsterdamDay(), content: '' })
const preview = ref(null)
const checking = ref(false)
const saving = ref(false)
const error = ref('')

const hasErrors = computed(() => !!preview.value?.errors.length)
const nothing = computed(
  () => preview.value && !preview.value.tasks.length && !preview.value.done.length
    && !preview.value.removed.length && !preview.value.meetings.length && !hasErrors.value,
)
const timeFmt = (d) => new Intl.DateTimeFormat('nl-NL', {
  weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam',
}).format(new Date(d))

onMounted(async () => {
  groups.value = await api('/pimpy/groups')
  if (groups.value.length === 1) form.value.group_id = groups.value[0].id
})

let timer
watch(() => [form.value.group_id, form.value.content], () => {
  clearTimeout(timer)
  timer = setTimeout(check, 500)
})

async function check() {
  if (!form.value.group_id || !form.value.content.trim()) {
    preview.value = null
    return
  }
  checking.value = true
  try {
    preview.value = await api('/pimpy/minutes/preview', {
      method: 'POST', body: { group_id: Number(form.value.group_id), content: form.value.content },
    })
    error.value = ''
  } catch (e) {
    error.value = e.message
  } finally {
    checking.value = false
  }
}

async function save() {
  error.value = ''
  saving.value = true
  try {
    const saved = await api('/pimpy/minutes', { method: 'POST', body: { ...form.value, group_id: Number(form.value.group_id) } })
    router.push(`/pimpy/notulen/${saved.id}`)
  } catch (e) {
    error.value = e.message
    await check()
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="editor-grid">
    <form class="card" @submit.prevent="save">
      <h2>Notulen toevoegen</h2>
      <div v-if="error" class="notice error">{{ error }}</div>
      <div class="grid-2">
        <label class="field">
          <span>Groep</span>
          <select v-model="form.group_id" required>
            <option value="" disabled>Kies een groep</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </label>
        <label class="field"><span>Datum vergadering</span><input v-model="form.minute_date" type="date" required /></label>
      </div>
      <label class="field">
        <span>Notulen</span>
        <textarea
          v-model="form.content"
          rows="18"
          required
          spellcheck="false"
          placeholder="Opening 13:30&#10;&#10;1. Stickermuur&#10;ACTIE Robin: nieuwe stickers bestellen&#10;&#10;DONE 1A&#10;MEETING 26-11-2026 13:30 Volgende vergadering"
        />
      </label>
      <div class="row">
        <button class="btn signal" :disabled="saving || hasErrors || !form.group_id">Opslaan</button>
        <RouterLink to="/pimpy/notulen" class="btn ghost">Annuleren</RouterLink>
        <span v-if="checking" class="small muted">Controleren…</span>
      </div>
    </form>

    <aside>
      <section v-if="preview" class="card check" :class="{ bad: hasErrors }">
        <h3>{{ hasErrors ? 'Eerst verbeteren' : 'Dit gebeurt bij opslaan' }}</h3>
        <ul v-if="hasErrors" class="errors">
          <li v-for="(e, i) in preview.errors" :key="i">
            <strong>Regel {{ e.line }}:</strong> {{ e.reason }}
            <code>{{ e.text }}</code>
          </li>
        </ul>
        <p v-if="nothing" class="muted small">Geen ACTIE-, DONE-, REMOVE- of MEETING-regels gevonden. De notulen worden gewoon opgeslagen.</p>
        <div v-if="preview.tasks.length">
          <h4>Nieuwe taken</h4>
          <ul>
            <li v-for="(t, i) in preview.tasks" :key="i">{{ t.title }} <span class="muted">→ {{ t.users.join(', ') }}</span></li>
          </ul>
        </div>
        <div v-if="preview.done.length">
          <h4>Afgerond</h4>
          <ul><li v-for="t in preview.done" :key="t.code"><span class="code">{{ t.code }}</span> {{ t.title }}</li></ul>
        </div>
        <div v-if="preview.removed.length">
          <h4>Vervallen</h4>
          <ul><li v-for="t in preview.removed" :key="t.code"><span class="code">{{ t.code }}</span> {{ t.title }}</li></ul>
        </div>
        <div v-if="preview.meetings.length">
          <h4>Op de agenda</h4>
          <ul><li v-for="(m, i) in preview.meetings" :key="i">{{ m.title }} <span class="muted">· {{ timeFmt(m.start_at) }}</span></li></ul>
        </div>
      </section>

      <section class="card help">
        <h3>Zo werkt het</h3>
        <p class="small muted">Eén opdracht per regel, in hoofdletters. Namen mogen kort of met een tikfout, zolang ze in de groep zitten. Taakcodes vind je bij <RouterLink to="/pimpy/taken">Taken</RouterLink>.</p>
        <dl>
          <template v-for="[code, uitleg] in SYNTAX_HELP" :key="code">
            <dt><code>{{ code }}</code></dt>
            <dd>{{ uitleg }}</dd>
          </template>
        </dl>
        <p class="small muted">Ook in het Nederlands: TAAK/TAKEN, KLAAR, VERVALT en VERGADERING. Datum van vandaag: {{ formatDate(amsterdamDay()) }}.</p>
      </section>
    </aside>
  </div>
</template>

<style scoped>
.editor-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 20px; align-items: start; }
@media (max-width: 900px) { .editor-grid { grid-template-columns: 1fr; } }
h2 { font-size: 1.9rem; }
h4 { font: 700 0.75rem var(--sans); text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin: 14px 0 6px; }
textarea { font: 0.95rem/1.6 ui-monospace, SFMono-Regular, Menlo, monospace; }
aside { display: grid; gap: 16px; }
.check { border-left: 4px solid var(--ok); }
.check.bad { border-left-color: var(--alarm); }
.check ul { padding-left: 1.1em; margin: 0; }
.check li { margin-bottom: 4px; }
.errors li { color: var(--alarm); }
.errors code { display: block; margin-top: 2px; color: var(--ink-soft); }
.code { font: 700 0.72rem ui-monospace, monospace; background: var(--ink); color: var(--paper); border-radius: 5px; padding: 1px 6px; }
code { font: 0.82rem ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--line); border-radius: 4px; padding: 1px 5px; word-break: break-word; }
.help dl { margin: 12px 0; }
.help dt { margin-top: 10px; }
.help dd { margin: 2px 0 0; font-size: 0.88rem; color: var(--ink-soft); }
</style>
