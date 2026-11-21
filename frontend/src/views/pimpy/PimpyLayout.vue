<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { auth } from '../../auth'

const route = useRoute()
const tabs = computed(() => [
  { to: '/pimpy/taken', label: 'Taken' },
  { to: '/pimpy/notulen', label: 'Notulen' },
  { to: '/pimpy/agenda', label: 'Agenda' },
  ...(auth.can('admin') ? [{ to: '/pimpy/groepen', label: 'Groepen' }] : []),
])
// Ook actief op subpagina's, bijv. /pimpy/notulen/4.
const isActive = (to) => route.path === to || route.path.startsWith(`${to}/`)
</script>

<template>
  <div class="wrap page">
    <span class="eyebrow">Notulen, taken en vergaderingen · alleen voor editors en admins</span>
    <h1>Pimpy</h1>
    <nav class="tabs" aria-label="Pimpy">
      <RouterLink
        v-for="t in tabs"
        :key="t.to"
        :to="t.to"
        :class="{ active: isActive(t.to) }"
        :aria-current="isActive(t.to) ? 'page' : undefined"
      >{{ t.label }}</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>

<style scoped>
.tabs { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 28px; border-bottom: 1px solid var(--line); }
.tabs a { padding: 10px 14px; font-weight: 600; text-decoration: none; color: var(--muted); border-bottom: 3px solid transparent; margin-bottom: -1px; }
.tabs a:hover { color: var(--ink); }
.tabs a.active { color: var(--ink); border-bottom-color: var(--signal); }
</style>
