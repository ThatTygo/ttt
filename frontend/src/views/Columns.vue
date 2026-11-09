<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../auth'
import ColumnCard from '../components/ColumnCard.vue'

const PAGE = 12
const route = useRoute()
const router = useRouter()

const q = ref(route.query.q || '')
const author = ref(route.query.auteur || '')
const items = ref([])
const authors = ref([])
const total = ref(0)
const loading = ref(false)

async function load(append = false) {
  loading.value = true
  const params = new URLSearchParams({ limit: PAGE, offset: append ? items.value.length : 0 })
  if (q.value) params.set('q', q.value)
  if (author.value) params.set('author', author.value)
  const data = await api(`/columns?${params}`)
  items.value = append ? [...items.value, ...data.items] : data.items
  authors.value = data.authors
  total.value = data.total
  loading.value = false
}

let timer
watch([q, author], () => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    router.replace({ query: { ...(q.value && { q: q.value }), ...(author.value && { auteur: author.value }) } })
    load()
  }, 250)
})
load()
</script>

<template>
  <div class="wrap page">
    <div class="row spread top">
      <div>
        <span class="eyebrow">Verslagen van de dagdienst</span>
        <h1>Columns</h1>
        <p class="lead">Elke avond (of nacht, of ochtend) het verslag van de dienstdoende teller. Op volgorde van verschijnen.</p>
      </div>
      <RouterLink v-if="auth.can('editor')" to="/columns/nieuw" class="btn signal">+ Nieuwe column</RouterLink>
    </div>

    <div class="filters">
      <label class="field">
        <span>Zoeken</span>
        <input v-model="q" type="search" placeholder="Bijv. ADE, Combino, Halloween…" />
      </label>
      <label class="field">
        <span>Teller</span>
        <select v-model="author">
          <option value="">Iedereen</option>
          <option v-for="a in authors" :key="a" :value="a">{{ a }}</option>
        </select>
      </label>
    </div>

    <p class="muted small">{{ total }} column{{ total === 1 ? '' : 's' }}</p>

    <div class="cards">
      <ColumnCard v-for="c in items" :key="c.id" :column="c" />
    </div>
    <p v-if="!loading && !items.length" class="card muted">Geen columns gevonden. Net als tramongelukken.</p>

    <div v-if="items.length < total" class="more">
      <button class="btn ghost" :disabled="loading" @click="load(true)">Meer laden</button>
    </div>
  </div>
</template>

<style scoped>
.top { align-items: end; margin-bottom: 24px; }
.filters { display: grid; grid-template-columns: 2fr 1fr; gap: 12px; }
@media (max-width: 560px) { .filters { grid-template-columns: 1fr; } }
.cards { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
.more { text-align: center; margin-top: 28px; }
</style>
