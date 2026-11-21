<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api'
import { ROLE_LABELS } from '../../auth'

const groups = ref([])
const users = ref([])
const editing = ref(null)
const error = ref('')

// Alleen goedgekeurde editors en admins kunnen in een groep (Pimpy is alleen voor hen).
const candidates = computed(() =>
  users.value.filter((u) => u.status === 'approved' && ['editor', 'admin'].includes(u.role)),
)

async function load() {
  ;[groups.value, users.value] = await Promise.all([api('/pimpy/groups'), api('/users')])
}
onMounted(load)

function open(group) {
  error.value = ''
  editing.value = group
    ? { id: group.id, name: group.name, description: group.description || '', member_ids: group.members.map((m) => m.id) }
    : { name: '', description: '', member_ids: [] }
}

async function save() {
  error.value = ''
  const { id, ...body } = editing.value
  try {
    if (id) await api(`/pimpy/groups/${id}`, { method: 'PUT', body })
    else await api('/pimpy/groups', { method: 'POST', body })
    editing.value = null
    await load()
  } catch (e) {
    error.value = e.message
  }
}

async function remove() {
  const g = editing.value
  if (!confirm(`Groep "${g.name}" verwijderen? Alle notulen, taken en vergaderingen van deze groep worden ook verwijderd. Dit kan niet ongedaan worden gemaakt.`)) return
  await api(`/pimpy/groups/${g.id}`, { method: 'DELETE' })
  editing.value = null
  await load()
}
</script>

<template>
  <div>
    <div class="row spread toolbar">
      <p class="muted small intro">Elke groep heeft eigen notulen, taken en vergaderingen. Leden van een groep zien alleen hun eigen groepen; admins zien alles.</p>
      <button class="btn signal sm" @click="open(null)">+ Groep</button>
    </div>

    <form v-if="editing" class="card edit" @submit.prevent="save">
      <h3>{{ editing.id ? `${editing.name} bewerken` : 'Nieuwe groep' }}</h3>
      <div v-if="error" class="notice error">{{ error }}</div>
      <div class="grid-2">
        <label class="field"><span>Naam</span><input v-model="editing.name" required maxlength="80" placeholder="Bijv. Bestuur" /></label>
        <label class="field"><span>Omschrijving (optioneel)</span><input v-model="editing.description" maxlength="300" /></label>
      </div>
      <fieldset class="field people">
        <span>Leden</span>
        <label v-for="u in candidates" :key="u.id" class="row check">
          <input v-model="editing.member_ids" type="checkbox" :value="u.id" />
          {{ u.name }} <span class="muted small">{{ ROLE_LABELS[u.role] }}</span>
        </label>
        <small v-if="!candidates.length" class="muted">Er zijn nog geen editors of admins. Geef iemand die rol onder Accounts.</small>
        <small v-else class="muted">Alleen editors en admins kunnen in een groep. Iemand anders toevoegen? Geef die eerst de rol editor onder <RouterLink to="/beheer/accounts">Accounts</RouterLink>.</small>
      </fieldset>
      <div class="row">
        <button class="btn signal">Opslaan</button>
        <button type="button" class="btn ghost" @click="editing = null">Annuleren</button>
        <button v-if="editing.id" type="button" class="btn danger push" @click="remove">Verwijderen</button>
      </div>
    </form>

    <p v-if="!groups.length" class="card muted">Nog geen groepen. Begin bijvoorbeeld met "Bestuur".</p>

    <div class="list">
      <article v-for="g in groups" :key="g.id" class="card group">
        <div class="row spread">
          <h3>{{ g.name }}</h3>
          <button class="btn sm ghost" @click="open(g)">Bewerken</button>
        </div>
        <p v-if="g.description" class="muted small">{{ g.description }}</p>
        <p class="small">{{ g.members.map((m) => m.name).join(', ') || 'Nog geen leden' }}</p>
      </article>
    </div>
  </div>
</template>

<style scoped>
.toolbar { margin-bottom: 20px; align-items: center; }
.intro { margin: 0; max-width: 60ch; }
.edit { margin-bottom: 24px; }
.people { border: 0; padding: 0; margin: 0 0 16px; display: flex; flex-wrap: wrap; gap: 8px 20px; }
.people > span { width: 100%; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); }
.people small { width: 100%; }
.check { flex-wrap: nowrap; gap: 8px; font-weight: 600; }
.push { margin-left: auto; }
.list { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.group h3 { margin: 0; }
.group p { margin: 8px 0 0; }
</style>
