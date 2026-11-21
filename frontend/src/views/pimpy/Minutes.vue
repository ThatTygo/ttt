<script setup>
import { onMounted, ref, watch } from 'vue'
import { api } from '../../api'
import { formatDate } from '../../format'

const groups = ref([])
const minutes = ref([])
const groupId = ref('')
const loading = ref(true)

async function load() {
  minutes.value = await api(`/pimpy/minutes${groupId.value ? `?group_id=${groupId.value}` : ''}`)
  loading.value = false
}

onMounted(async () => {
  groups.value = await api('/pimpy/groups')
  await load()
})
watch(groupId, load)
</script>

<template>
  <div>
    <div class="row spread toolbar">
      <select v-model="groupId" aria-label="Groep">
        <option value="">Alle groepen</option>
        <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
      <RouterLink v-if="groups.length" to="/pimpy/notulen/nieuw" class="btn signal sm">+ Notulen toevoegen</RouterLink>
    </div>

    <p v-if="!loading && !minutes.length" class="card muted">Nog geen notulen.</p>

    <div class="list">
      <RouterLink v-for="m in minutes" :key="m.id" :to="`/pimpy/notulen/${m.id}`" class="card minute">
        <div class="row spread">
          <strong class="date">{{ formatDate(m.minute_date) }}</strong>
          <span class="badge">{{ m.group.name }}</span>
        </div>
        <p class="muted small excerpt">{{ m.excerpt }}</p>
        <span class="small muted">
          {{ m.task_count }} {{ m.task_count === 1 ? 'taak' : 'taken' }}
          <template v-if="m.created_by"> · ingevoerd door {{ m.created_by }}</template>
        </span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.toolbar { margin-bottom: 20px; }
.toolbar select { width: auto; }
.list { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
.minute { text-decoration: none; display: grid; gap: 6px; padding: 18px 20px; transition: border-color 0.15s ease; }
.minute:hover { border-color: var(--signal); }
.date { font-family: var(--display); font-weight: 400; font-size: 1.5rem; letter-spacing: 0.02em; }
.excerpt { margin: 0; }
</style>
