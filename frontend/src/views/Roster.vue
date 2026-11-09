<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { DAYS, auth } from '../auth'

const roster = ref([])
const todayIndex = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(
  new Intl.DateTimeFormat('en-GB', { weekday: 'short', timeZone: 'Europe/Amsterdam' }).format(new Date()),
)

onMounted(async () => {
  roster.value = await api('/roster')
})
</script>

<template>
  <div class="wrap page">
    <span class="eyebrow">Alleen zichtbaar voor editors en admins</span>
    <h1>Dienstrooster</h1>
    <p class="lead">
      Wie houdt welke dagdienst? De dienstdoende teller speurt het nieuws af en sluit de dag af met een column.
    </p>

    <ol class="roster">
      <li v-for="r in roster" :key="r.day" :class="{ today: r.day === todayIndex }">
        <span class="day">{{ DAYS[r.day] }}</span>
        <span class="who">{{ r.names.join(' & ') || '—' }}</span>
        <span v-if="r.day === todayIndex" class="badge signal">Vandaag</span>
      </li>
    </ol>

    <p class="muted small">
      <template v-if="auth.can('admin')">Dagdiensten wijzig je in de <RouterLink to="/leden">ledenadministratie</RouterLink>.</template>
      <template v-else>Klopt er iets niet? Vraag een admin om het rooster aan te passen.</template>
    </p>
  </div>
</template>

<style scoped>
.roster { list-style: none; padding: 0; margin: 28px 0 20px; display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }
.roster li { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 16px; display: grid; gap: 6px; align-content: start; min-height: 110px; }
.roster li.today { border-color: var(--signal); box-shadow: 0 0 0 2px var(--signal); }
.day { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); font-weight: 700; }
.who { font-family: var(--display); font-size: 1.7rem; letter-spacing: 0.03em; line-height: 1.1; }
.badge { justify-self: start; }
@media (max-width: 900px) { .roster { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); } }
</style>
