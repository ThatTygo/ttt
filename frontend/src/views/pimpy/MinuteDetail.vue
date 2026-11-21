<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../api'
import { auth } from '../../auth'
import { formatDate } from '../../format'
import { STATUS_LABELS } from '../../pimpy'

const props = defineProps({ id: String })
const router = useRouter()
const minute = ref(null)
const error = ref('')

// Per regelnummer de taken die eruit zijn voortgekomen.
const tasksByLine = computed(() => {
  const map = {}
  for (const t of minute.value?.tasks || []) (map[t.line] ||= []).push(t)
  return map
})
const lines = computed(() => (minute.value ? minute.value.content.split('\n') : []))
const timeFmt = (d) => new Intl.DateTimeFormat('nl-NL', {
  weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam',
}).format(new Date(d))

watch(() => props.id, async (id) => {
  try {
    minute.value = await api(`/pimpy/minutes/${id}`)
  } catch (e) {
    error.value = e.message
  }
}, { immediate: true })

async function remove() {
  const n = minute.value.tasks.length
  if (!confirm(`Deze notulen verwijderen?${n ? ` De ${n} taken die eruit zijn voortgekomen worden ook verwijderd.` : ''} Dit kan niet ongedaan worden gemaakt.`)) return
  await api(`/pimpy/minutes/${props.id}`, { method: 'DELETE' })
  router.push('/pimpy/notulen')
}
</script>

<template>
  <div>
    <RouterLink to="/pimpy/notulen" class="back small">← Alle notulen</RouterLink>
    <div v-if="error" class="notice error">{{ error }}</div>

    <template v-if="minute">
      <div class="row spread head">
        <div>
          <span class="badge">{{ minute.group.name }}</span>
          <h2>Notulen {{ formatDate(minute.minute_date) }}</h2>
          <p v-if="minute.created_by" class="small muted">Ingevoerd door {{ minute.created_by }} op {{ formatDate(minute.created_at, true) }}</p>
        </div>
        <button v-if="auth.can('admin')" class="btn sm danger" @click="remove">Verwijderen</button>
      </div>

      <div class="layout">
        <ol class="card text">
          <li v-for="(l, i) in lines" :key="i" :class="{ hit: tasksByLine[i + 1] }">
            <span class="txt">{{ l || ' ' }}</span>
            <span v-for="t in tasksByLine[i + 1] || []" :key="t.id" class="code" :title="t.users.map((u) => u.name).join(', ')">{{ t.code }}</span>
          </li>
        </ol>

        <aside>
          <section class="card">
            <h3>Taken uit deze notulen</h3>
            <p v-if="!minute.tasks.length" class="small muted">Geen.</p>
            <ul class="tasks">
              <li v-for="t in minute.tasks" :key="t.id">
                <span class="code">{{ t.code }}</span>
                <div>
                  {{ t.title }}
                  <div class="small muted">{{ t.users.map((u) => u.name).join(', ') }} · {{ STATUS_LABELS[t.status] }}</div>
                </div>
              </li>
            </ul>
          </section>
          <section v-if="minute.meetings.length" class="card">
            <h3>Op de agenda gezet</h3>
            <ul class="plain">
              <li v-for="m in minute.meetings" :key="m.id">{{ m.title }}<div class="small muted">{{ timeFmt(m.start_at) }}</div></li>
            </ul>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 16px; text-decoration: none; color: var(--muted); }
.head { align-items: end; margin-bottom: 20px; }
h2 { margin-top: 10px; }
.layout { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr); gap: 20px; align-items: start; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
.text { margin: 0; padding: 16px 16px 16px 52px; font: 0.92rem/1.7 ui-monospace, SFMono-Regular, Menlo, monospace; overflow-x: auto; }
.text li { padding-left: 6px; white-space: pre-wrap; word-break: break-word; }
.text li::marker { color: var(--muted); font-size: 0.78rem; }
.text li.hit { background: color-mix(in srgb, var(--signal) 22%, transparent); border-radius: 4px; }
.code { font: 700 0.72rem ui-monospace, monospace; background: var(--ink); color: var(--paper); border-radius: 5px; padding: 1px 6px; margin-left: 8px; white-space: nowrap; }
aside { display: grid; gap: 16px; }
.tasks, .plain { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.tasks li { display: flex; gap: 8px; align-items: baseline; }
.tasks .code { margin-left: 0; }
</style>
