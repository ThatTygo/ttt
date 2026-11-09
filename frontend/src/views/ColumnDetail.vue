<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../auth'
import { formatDate, paragraphs } from '../format'

const props = defineProps({ id: String })
const router = useRouter()
const column = ref(null)
const error = ref('')

const body = computed(() => (column.value ? paragraphs(column.value.body) : []))

watch(
  () => props.id,
  async (id) => {
    error.value = ''
    try {
      column.value = await api(`/columns/${id}`)
      document.title = `${column.value.title} · Trauma Tram Tellers`
    } catch (e) {
      error.value = e.message
    }
  },
  { immediate: true },
)

async function remove() {
  if (!confirm(`Column "${column.value.title}" verwijderen? Dit kan niet ongedaan worden gemaakt.`)) return
  await api(`/columns/${props.id}`, { method: 'DELETE' })
  router.push('/columns')
}
</script>

<template>
  <div class="narrow page">
    <RouterLink to="/columns" class="back small">← Alle columns</RouterLink>

    <div v-if="error" class="notice error">{{ error }}</div>

    <article v-else-if="column">
      <header class="head">
        <span class="badge signal">Dagdienst van {{ column.author_name }}</span>
        <h1>{{ column.title }}</h1>
        <p class="muted small">
          <time :datetime="column.published_at">{{ formatDate(column.published_at, true) }}</time>
        </p>
        <div v-if="auth.can('editor')" class="row">
          <RouterLink :to="`/columns/${column.id}/bewerken`" class="btn sm ghost">Bewerken</RouterLink>
          <button class="btn sm danger" @click="remove">Verwijderen</button>
        </div>
      </header>

      <div class="prose">
        <p v-for="(p, i) in body" :key="i">{{ p }}</p>
      </div>

      <footer class="sign">
        <span class="muted small">Geschreven door</span>
        <strong>{{ column.author_name }}</strong>
      </footer>
    </article>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 24px; text-decoration: none; color: var(--muted); }
.head { border-bottom: 1px solid var(--line); padding-bottom: 20px; margin-bottom: 28px; }
.head h1 { margin-top: 14px; }
.prose p:first-child::first-letter {
  float: left;
  font-family: var(--display);
  font-size: 4.2em;
  line-height: 0.8;
  padding: 6px 8px 0 0;
  color: var(--ink);
}
.sign { margin-top: 32px; padding-top: 20px; border-top: 3px solid var(--ink); display: flex; gap: 10px; align-items: baseline; }
.sign strong { font-family: var(--display); font-size: 1.6rem; font-weight: 400; letter-spacing: 0.03em; }
</style>
