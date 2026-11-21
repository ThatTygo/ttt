<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../../api'
import { toLocalInput } from '../../format'

const groups = ref([])
const meetings = ref([])
const past = ref(false)
const adding = ref(null)
const error = ref('')

const dayFmt = new Intl.DateTimeFormat('nl-NL', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Amsterdam' })
const timeFmt = new Intl.DateTimeFormat('nl-NL', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' })

// Vergaderingen gegroepeerd per dag.
const days = computed(() => {
  const out = []
  for (const m of meetings.value) {
    const day = dayFmt.format(new Date(m.start_at))
    if (out.at(-1)?.day !== day) out.push({ day, items: [] })
    out.at(-1).items.push(m)
  }
  return out
})

async function load() {
  meetings.value = await api(`/pimpy/meetings?past=${past.value}`)
}
onMounted(async () => {
  groups.value = await api('/pimpy/groups')
  await load()
})
watch(past, load)

function startAdd() {
  adding.value = { group_id: groups.value[0]?.id || '', title: '', start_at: toLocalInput().slice(0, 11) + '20:00', hours: 1 }
}

async function saveAdd() {
  error.value = ''
  try {
    await api('/pimpy/meetings', {
      method: 'POST',
      body: { ...adding.value, group_id: Number(adding.value.group_id), hours: Number(adding.value.hours) },
    })
    adding.value = null
    await load()
  } catch (e) {
    error.value = e.message
  }
}

async function remove(m) {
  if (!confirm(`"${m.title}" van de agenda halen?`)) return
  await api(`/pimpy/meetings/${m.id}`, { method: 'DELETE' })
  await load()
}
</script>

<template>
  <div>
    <div class="row spread toolbar">
      <div class="seg" role="group" aria-label="Periode">
        <button :class="{ on: !past }" @click="past = false">Komend</button>
        <button :class="{ on: past }" @click="past = true">Geweest</button>
      </div>
      <button v-if="groups.length" class="btn signal sm" @click="startAdd">+ Vergadering</button>
    </div>

    <div v-if="error" class="notice error">{{ error }}</div>

    <form v-if="adding" class="card add" @submit.prevent="saveAdd">
      <h3>Nieuwe vergadering</h3>
      <div class="grid-2">
        <label class="field">
          <span>Groep</span>
          <select v-model="adding.group_id" required>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </label>
        <label class="field"><span>Titel</span><input v-model="adding.title" required maxlength="200" /></label>
        <label class="field"><span>Begint</span><input v-model="adding.start_at" type="datetime-local" required /></label>
        <label class="field"><span>Duur (uren)</span><input v-model="adding.hours" type="number" min="0.5" max="99" step="0.5" required /></label>
      </div>
      <div class="row">
        <button class="btn signal">Toevoegen</button>
        <button type="button" class="btn ghost" @click="adding = null">Annuleren</button>
      </div>
    </form>

    <p v-if="!days.length" class="card muted">
      {{ past ? 'Nog geen vergaderingen geweest.' : 'Geen vergaderingen gepland. Zet ze in de notulen met een MEETING-regel, of voeg ze hier toe.' }}
    </p>

    <section v-for="d in days" :key="d.day" class="day">
      <h3>{{ d.day }}</h3>
      <article v-for="m in d.items" :key="m.id" class="card meeting">
        <div class="time">{{ timeFmt.format(new Date(m.start_at)) }}<span class="muted"> – {{ timeFmt.format(new Date(m.end_at)) }}</span></div>
        <div class="what">
          <strong>{{ m.title }}</strong>
          <div class="small muted">
            {{ m.group.name }}
            <template v-if="m.minute_id"> · uit de <RouterLink :to="`/pimpy/notulen/${m.minute_id}`">notulen</RouterLink></template>
          </div>
        </div>
        <button class="btn sm ghost" @click="remove(m)">Verwijderen</button>
      </article>
    </section>
  </div>
</template>

<style scoped>
.toolbar { margin-bottom: 20px; }
.seg { display: flex; gap: 4px; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
.seg button { border: 0; background: none; color: var(--muted); font: 600 0.85rem var(--sans); padding: 6px 14px; border-radius: 999px; cursor: pointer; }
.seg button.on { background: var(--ink); color: var(--paper); }
.add { margin-bottom: 24px; }
.day { margin-bottom: 24px; }
.day h3 { font-size: 1.4rem; text-transform: capitalize; }
.meeting { display: flex; gap: 18px; align-items: center; padding: 14px 18px; margin-bottom: 8px; flex-wrap: wrap; }
.time { font-family: var(--display); font-size: 1.5rem; letter-spacing: 0.03em; min-width: 7.5ch; }
.what { flex: 1; min-width: 180px; }
</style>
