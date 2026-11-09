<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { DAYS, auth } from '../auth'
import { formatDate } from '../format'

const members = ref([])
const users = ref([])
const editing = ref(null) // null = dicht, {} = nieuw, {id..} = bewerken
const error = ref('')

const isAdmin = computed(() => auth.can('admin'))
const active = computed(() => members.value.filter((m) => m.active))
const todayIndex = (['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']).indexOf(
  new Intl.DateTimeFormat('en-GB', { weekday: 'short', timeZone: 'Europe/Amsterdam' }).format(new Date()),
)
const roster = computed(() =>
  DAYS.map((day, i) => ({ day, i, names: active.value.filter((m) => m.shift_day === i).map((m) => m.name) })),
)
const userName = (id) => users.value.find((u) => u.id === id)?.name

async function load() {
  members.value = await api('/members')
  if (isAdmin.value) users.value = await api('/users')
}
onMounted(load)

function open(member) {
  error.value = ''
  editing.value = member
    ? { ...member, shift_day: member.shift_day ?? '', member_since: member.member_since ?? '', user_id: member.user_id ?? '' }
    : { name: '', nickname: '', function: '', shift_day: '', member_since: '', active: true, notes: '', user_id: '' }
}

async function save() {
  const m = editing.value
  const body = {
    name: m.name,
    nickname: m.nickname || null,
    function: m.function || null,
    shift_day: m.shift_day === '' ? null : Number(m.shift_day),
    member_since: m.member_since || null,
    active: m.active,
    notes: m.notes || null,
    user_id: m.user_id === '' ? null : Number(m.user_id),
  }
  try {
    if (m.id) await api(`/members/${m.id}`, { method: 'PUT', body })
    else await api('/members', { method: 'POST', body })
    editing.value = null
    await load()
  } catch (e) {
    error.value = e.message
  }
}

async function remove(m) {
  if (!confirm(`${m.name} uit de ledenadministratie verwijderen? Dit kan niet ongedaan worden gemaakt.`)) return
  await api(`/members/${m.id}`, { method: 'DELETE' })
  editing.value = null
  await load()
}
</script>

<template>
  <div class="wrap page">
    <div class="row spread top">
      <div>
        <span class="eyebrow">Alleen zichtbaar voor admins</span>
        <h1>Ledenadministratie</h1>
        <p class="lead">Wie er bij de TTT hoort, wie welke dagdienst draait en wie welke functie bekleedt.</p>
      </div>
      <button v-if="isAdmin" class="btn signal" @click="open(null)">+ Lid toevoegen</button>
    </div>

    <section class="roster">
      <h2>Dienstrooster</h2>
      <ol>
        <li v-for="r in roster" :key="r.day" :class="{ today: r.i === todayIndex }">
          <span class="day">{{ r.day }}</span>
          <span class="who">{{ r.names.join(' & ') || '—' }}</span>
          <span v-if="r.i === todayIndex" class="badge signal">Vandaag</span>
        </li>
      </ol>
    </section>

    <form v-if="editing" class="card editor" @submit.prevent="save">
      <h3>{{ editing.id ? `${editing.name} bewerken` : 'Nieuw lid' }}</h3>
      <div v-if="error" class="notice error">{{ error }}</div>
      <div class="grid-2">
        <label class="field"><span>Naam</span><input v-model="editing.name" required maxlength="80" /></label>
        <label class="field"><span>Bijnaam</span><input v-model="editing.nickname" maxlength="80" /></label>
        <label class="field"><span>Functie</span><input v-model="editing.function" maxlength="80" placeholder="Bijv. Voorzitter" /></label>
        <label class="field">
          <span>Dagdienst</span>
          <select v-model="editing.shift_day">
            <option value="">Geen vaste dag</option>
            <option v-for="(d, i) in DAYS" :key="d" :value="i">{{ d }}</option>
          </select>
        </label>
        <label class="field"><span>Lid sinds</span><input v-model="editing.member_since" type="date" /></label>
        <label class="field">
          <span>Gekoppeld account</span>
          <select v-model="editing.user_id">
            <option value="">Geen</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }} ({{ u.email }})</option>
          </select>
        </label>
      </div>
      <label class="field">
        <span>Notities</span>
        <textarea v-model="editing.notes" rows="3" maxlength="2000" />
        <small>Zet hier geen gevoelige gegevens in (zie privacybeleid).</small>
      </label>
      <label class="row check"><input v-model="editing.active" type="checkbox" /> Actief lid</label>
      <div class="row">
        <button class="btn signal">Opslaan</button>
        <button type="button" class="btn ghost" @click="editing = null">Annuleren</button>
        <button v-if="editing.id" type="button" class="btn danger push" @click="remove(editing)">Verwijderen</button>
      </div>
    </form>

    <div class="card table-scroll">
      <table>
        <thead>
          <tr>
            <th>Naam</th>
            <th>Functie</th>
            <th>Dagdienst</th>
            <th>Lid sinds</th>
            <th v-if="isAdmin">Account</th>
            <th v-if="isAdmin" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in members" :key="m.id" :class="{ inactive: !m.active }">
            <td>
              <strong>{{ m.name }}</strong>
              <span v-if="m.nickname" class="muted"> “{{ m.nickname }}”</span>
              <span v-if="!m.active" class="badge">Oud-lid</span>
              <div v-if="isAdmin && m.notes" class="small muted note">{{ m.notes }}</div>
            </td>
            <td>{{ m.function || '—' }}</td>
            <td>{{ m.shift_day != null ? DAYS[m.shift_day] : '—' }}</td>
            <td>{{ m.member_since ? formatDate(m.member_since) : 'Vanaf het begin' }}</td>
            <td v-if="isAdmin" class="small">{{ userName(m.user_id) || '—' }}</td>
            <td v-if="isAdmin"><button class="btn sm ghost" @click="open(m)">Bewerken</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.top { align-items: end; margin-bottom: 28px; }
.roster { margin-bottom: 28px; }
.roster ol { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
.roster li { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px; display: grid; gap: 4px; align-content: start; }
.roster li.today { border-color: var(--signal); box-shadow: 0 0 0 2px var(--signal); }
.day { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); font-weight: 700; }
.who { font-family: var(--display); font-size: 1.5rem; letter-spacing: 0.03em; line-height: 1.1; }
.roster .badge { justify-self: start; }
@media (max-width: 900px) { .roster ol { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); } }

.editor { margin-bottom: 24px; }
.check { margin-bottom: 18px; font-weight: 600; }
.push { margin-left: auto; }
tr.inactive td { opacity: 0.6; }
.note { margin-top: 4px; white-space: pre-line; }
</style>
