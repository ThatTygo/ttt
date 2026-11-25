<script setup>
import { onMounted, ref, watch } from 'vue'
import { api } from '../api'
import { auth } from '../auth'
import { formatDate } from '../format'
import { KIND_LABELS, PRIORITY_LABELS, STATUS_LABELS } from '../tickets'

const isAdmin = auth.can('admin')
const scope = ref(isAdmin ? 'all' : 'mine')
const filter = ref('open')
const tickets = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  const params = new URLSearchParams({ scope: scope.value })
  if (filter.value) params.set('status', filter.value)
  tickets.value = await api(`/tickets?${params}`)
  loading.value = false
}
onMounted(load)
watch([scope, filter], load)
</script>

<template>
  <div class="wrap page">
    <span class="eyebrow">Bugs, ideeën en vragen over de site</span>
    <h1>{{ isAdmin && scope === 'all' ? 'Meldingen' : 'Mijn meldingen' }}</h1>
    <p class="lead">Gebruik de knop <strong>Melden</strong> rechtsonder om iets te melden, op elke pagina.</p>

    <div class="toolbar">
      <div v-if="isAdmin" class="seg" role="group" aria-label="Welke meldingen">
        <button :class="{ on: scope === 'all' }" @click="scope = 'all'">Alle</button>
        <button :class="{ on: scope === 'mine' }" @click="scope = 'mine'">Van mij</button>
      </div>
      <div class="seg" role="group" aria-label="Status">
        <button :class="{ on: filter === 'open' }" @click="filter = 'open'">Open</button>
        <button :class="{ on: filter === 'closed' }" @click="filter = 'closed'">Afgehandeld</button>
        <button :class="{ on: filter === '' }" @click="filter = ''">Alles</button>
      </div>
    </div>

    <p v-if="!loading && !tickets.length" class="card muted">
      {{ filter === 'open' ? 'Geen openstaande meldingen.' : 'Geen meldingen.' }}
    </p>

    <div class="list">
      <RouterLink v-for="t in tickets" :key="t.id" :to="`/meldingen/${t.id}`" class="card ticket">
        <div class="row spread top">
          <span class="row tags">
            <span class="badge">#{{ t.id }}</span>
            <span class="badge" :class="`kind-${t.kind}`">{{ KIND_LABELS[t.kind] }}</span>
            <span class="badge" :class="`st-${t.status}`">{{ STATUS_LABELS[t.status] }}</span>
            <span v-if="isAdmin && t.priority !== 'normaal'" class="badge" :class="`pr-${t.priority}`">{{ PRIORITY_LABELS[t.priority] }}</span>
          </span>
          <span class="small muted">{{ formatDate(t.updated_at, true) }}</span>
        </div>
        <strong class="title">{{ t.title }}</strong>
        <span class="small muted">
          <template v-if="isAdmin">{{ t.reporter?.name || 'Verwijderd account' }} · </template>
          {{ t.message_count }} {{ t.message_count === 1 ? 'reactie' : 'reacties' }}
          <template v-if="t.assignee"> · behandelaar: {{ t.assignee.name }}</template>
        </span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.toolbar { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.seg { display: flex; gap: 4px; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
.seg button { border: 0; background: none; color: var(--muted); font: 600 0.85rem var(--sans); padding: 6px 14px; border-radius: 999px; cursor: pointer; }
.seg button.on { background: var(--ink); color: var(--paper); }
.list { display: grid; gap: 10px; }
.ticket { display: grid; gap: 6px; text-decoration: none; padding: 16px 20px; transition: border-color 0.15s ease; }
.ticket:hover { border-color: var(--signal); }
.top { gap: 8px; }
.tags { gap: 6px; }
.title { font-size: 1.05rem; overflow-wrap: anywhere; }
</style>

<style>
/* Gedeeld met TicketDetail. */
.badge.kind-bug { background: color-mix(in srgb, var(--alarm) 22%, transparent); }
.badge.kind-idee { background: color-mix(in srgb, var(--signal) 30%, transparent); }
.badge.st-open { background: var(--signal); color: var(--signal-ink); }
.badge.st-in_behandeling { background: color-mix(in srgb, var(--signal) 30%, transparent); }
.badge.st-opgelost { background: var(--ok); color: #fff; }
.badge.pr-hoog { background: color-mix(in srgb, var(--alarm) 30%, transparent); }
.badge.pr-urgent { background: var(--alarm); color: #fff; }
</style>
