<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { ROLE_LABELS } from '../auth'
import UserAvatar from '../components/UserAvatar.vue'

const profiles = ref([])
const q = ref('')
const shown = computed(() => {
  const term = q.value.trim().toLowerCase()
  return term ? profiles.value.filter((p) => p.name.toLowerCase().includes(term)) : profiles.value
})

onMounted(async () => {
  profiles.value = await api('/profiles')
})
</script>

<template>
  <div class="wrap page">
    <span class="eyebrow">Alleen zichtbaar voor ingelogde leden</span>
    <h1>Wie is wie</h1>
    <p class="lead">Alle leden met een account op de site.</p>

    <label class="field search">
      <span>Zoeken</span>
      <input v-model="q" type="search" placeholder="Naam…" />
    </label>

    <div class="grid">
      <RouterLink v-for="p in shown" :key="p.id" :to="`/profiel/${p.id}`" class="card person">
        <UserAvatar :user="p" :size="72" />
        <div class="who">
          <strong>{{ p.name }}</strong>
          <span class="small muted">{{ ROLE_LABELS[p.role] }}</span>
          <p v-if="p.bio" class="small muted bio">{{ p.bio }}</p>
        </div>
      </RouterLink>
    </div>
    <p v-if="profiles.length && !shown.length" class="card muted">Niemand gevonden.</p>
  </div>
</template>

<style scoped>
.search { max-width: 360px; }
.grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.person { display: flex; gap: 14px; align-items: center; text-decoration: none; padding: 16px; transition: border-color 0.15s ease; }
.person:hover { border-color: var(--signal); }
.who { display: grid; gap: 2px; min-width: 0; }
.who strong { overflow-wrap: anywhere; }
.bio { margin: 4px 0 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
