<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '../../api'
import { auth } from '../../auth'
import { formatDate } from '../../format'
import { CLOSED_STATUSES, OPEN_STATUSES, STATUS_LABELS } from '../../pimpy'

const groups = ref([])
const tasks = ref([])
const scope = ref('mine')
const groupId = ref('')
const showClosed = ref(false)
const error = ref('')
const loading = ref(true)
const openId = ref(null) // uitgeklapte taak
const edit = ref(null)
const adding = ref(null)

const columns = computed(() =>
  OPEN_STATUSES.map((status) => ({ status, items: tasks.value.filter((t) => t.status === status) })),
)
const closed = computed(() => tasks.value.filter((t) => CLOSED_STATUSES.includes(t.status)))
const groupById = (id) => groups.value.find((g) => g.id === Number(id))

async function load() {
  loading.value = true
  const params = new URLSearchParams({ scope: scope.value, include_closed: showClosed.value })
  if (groupId.value) params.set('group_id', groupId.value)
  tasks.value = await api(`/pimpy/tasks?${params}`)
  loading.value = false
}

onMounted(async () => {
  groups.value = await api('/pimpy/groups')
  await load()
})
watch([scope, groupId, showClosed], load)

async function setStatus(task, status) {
  error.value = ''
  try {
    Object.assign(task, await api(`/pimpy/tasks/${task.id}`, { method: 'PATCH', body: { status } }))
  } catch (e) {
    error.value = e.message
  }
}

function toggle(task) {
  openId.value = openId.value === task.id ? null : task.id
  edit.value = null
}

function startEdit(task) {
  edit.value = { id: task.id, title: task.title, content: task.content || '', user_ids: task.users.map((u) => u.id) }
}

async function saveEdit(task) {
  error.value = ''
  try {
    const { title, content, user_ids } = edit.value
    Object.assign(task, await api(`/pimpy/tasks/${task.id}`, { method: 'PATCH', body: { title, content, user_ids } }))
    edit.value = null
  } catch (e) {
    error.value = e.message
  }
}

function startAdd() {
  const first = groups.value[0]
  adding.value = { group_id: groupId.value || first?.id || '', title: '', content: '', user_ids: [auth.user.id] }
}

async function saveAdd() {
  error.value = ''
  try {
    await api('/pimpy/tasks', { method: 'POST', body: { ...adding.value, group_id: Number(adding.value.group_id) } })
    adding.value = null
    await load()
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div>
    <div class="toolbar">
      <div class="seg" role="group" aria-label="Welke taken">
        <button :class="{ on: scope === 'mine' }" @click="scope = 'mine'">Mijn taken</button>
        <button :class="{ on: scope === 'all' }" @click="scope = 'all'">Alle taken</button>
      </div>
      <select v-model="groupId" aria-label="Groep">
        <option value="">Alle groepen</option>
        <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
      <label class="row small check"><input v-model="showClosed" type="checkbox" /> Toon afgerond en vervallen</label>
      <button v-if="groups.length" class="btn signal sm push" @click="startAdd">+ Taak</button>
    </div>

    <div v-if="error" class="notice error">{{ error }}</div>

    <p v-if="!groups.length && !loading" class="card muted">
      Je zit nog in geen enkele groep. <template v-if="auth.can('admin')">Maak er een aan onder <RouterLink to="/pimpy/groepen">Groepen</RouterLink>.</template>
      <template v-else>Vraag een admin om je aan een groep toe te voegen.</template>
    </p>

    <form v-if="adding" class="card add" @submit.prevent="saveAdd">
      <h3>Nieuwe taak</h3>
      <div class="grid-2">
        <label class="field">
          <span>Groep</span>
          <select v-model="adding.group_id" required @change="adding.user_ids = []">
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </label>
        <label class="field"><span>Taak</span><input v-model="adding.title" required maxlength="500" /></label>
      </div>
      <label class="field"><span>Toelichting (optioneel)</span><textarea v-model="adding.content" rows="2" maxlength="5000" /></label>
      <fieldset class="field people">
        <span>Voor wie</span>
        <label v-for="u in groupById(adding.group_id)?.members || []" :key="u.id" class="row check">
          <input v-model="adding.user_ids" type="checkbox" :value="u.id" /> {{ u.name }}
        </label>
      </fieldset>
      <div class="row">
        <button class="btn signal" :disabled="!adding.user_ids.length">Toevoegen</button>
        <button type="button" class="btn ghost" @click="adding = null">Annuleren</button>
      </div>
    </form>

    <div v-if="groups.length" class="board">
      <section v-for="col in columns" :key="col.status" class="column" :class="col.status">
        <h3>{{ STATUS_LABELS[col.status] }} <span class="count">{{ col.items.length }}</span></h3>
        <p v-if="!col.items.length" class="small muted empty">Niks</p>
        <article v-for="t in col.items" :key="t.id" class="task" :class="{ open: openId === t.id }">
          <button class="task-head" @click="toggle(t)">
            <span class="code">{{ t.code }}</span>
            <span class="title">{{ t.title }}</span>
          </button>
          <div class="meta small muted">
            {{ t.users.map((u) => u.name).join(', ') || 'Niemand' }} · {{ t.group.name }}
          </div>
          <div v-if="openId === t.id" class="detail">
            <p v-if="t.content" class="content">{{ t.content }}</p>
            <p class="small muted">
              <template v-if="t.minute_id">
                Uit de <RouterLink :to="`/pimpy/notulen/${t.minute_id}`">notulen van {{ formatDate(t.minute_date) }}</RouterLink>, regel {{ t.line }}.
              </template>
              <template v-else>Handmatig toegevoegd op {{ formatDate(t.created_at) }}.</template>
            </p>
            <form v-if="edit?.id === t.id" class="edit" @submit.prevent="saveEdit(t)">
              <label class="field"><span>Taak</span><input v-model="edit.title" required maxlength="500" /></label>
              <label class="field"><span>Toelichting</span><textarea v-model="edit.content" rows="2" maxlength="5000" /></label>
              <fieldset class="field people">
                <span>Voor wie</span>
                <label v-for="u in groupById(t.group.id)?.members || []" :key="u.id" class="row check">
                  <input v-model="edit.user_ids" type="checkbox" :value="u.id" /> {{ u.name }}
                </label>
              </fieldset>
              <div class="row">
                <button class="btn sm signal" :disabled="!edit.user_ids.length">Opslaan</button>
                <button type="button" class="btn sm ghost" @click="edit = null">Annuleren</button>
              </div>
            </form>
            <button v-else class="btn sm ghost" @click="startEdit(t)">Bewerken</button>
          </div>
          <select class="status" :value="t.status" :aria-label="`Status van ${t.title}`" @change="setStatus(t, $event.target.value)">
            <option v-for="(label, s) in STATUS_LABELS" :key="s" :value="s">{{ label }}</option>
          </select>
        </article>
      </section>
    </div>

    <section v-if="showClosed && closed.length" class="closed">
      <h3>Afgerond en vervallen</h3>
      <div class="card table-scroll">
        <table>
          <tbody>
            <tr v-for="t in closed" :key="t.id">
              <td><span class="code">{{ t.code }}</span></td>
              <td>{{ t.title }}<div class="small muted">{{ t.users.map((u) => u.name).join(', ') || 'Niemand' }} · {{ t.group.name }}</div></td>
              <td>
                <select :value="t.status" :aria-label="`Status van ${t.title}`" @change="setStatus(t, $event.target.value)">
                  <option v-for="(label, s) in STATUS_LABELS" :key="s" :value="s">{{ label }}</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 20px; }
.toolbar select { width: auto; }
.push { margin-left: auto; }
.check { font-weight: 600; flex-wrap: nowrap; gap: 8px; }
.seg { display: flex; gap: 4px; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 3px; }
.seg button { border: 0; background: none; color: var(--muted); font: 600 0.85rem var(--sans); padding: 6px 14px; border-radius: 999px; cursor: pointer; }
.seg button.on { background: var(--ink); color: var(--paper); }

.add { margin-bottom: 24px; }
.people { border: 0; padding: 0; margin: 0 0 16px; display: flex; flex-wrap: wrap; gap: 6px 18px; }
.people > span { width: 100%; font-size: 0.85rem; font-weight: 600; color: var(--ink-soft); }

.board { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; align-items: start; }
@media (max-width: 980px) { .board { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .board { grid-template-columns: 1fr; } }
.column { background: color-mix(in srgb, var(--surface) 60%, transparent); border: 1px solid var(--line); border-radius: var(--radius); padding: 12px; border-top: 4px solid var(--line); }
.column.started { border-top-color: var(--signal); }
.column.done { border-top-color: var(--ok); }
.column.not_done { border-top-color: var(--alarm); }
.column h3 { font-size: 1.3rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.count { font: 700 0.75rem var(--sans); background: var(--line); border-radius: 999px; padding: 1px 8px; }
.empty { margin: 4px 2px 8px; }

.task { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; box-shadow: var(--shadow); }
.task.open { border-color: var(--signal); }
.task-head { display: flex; gap: 8px; align-items: baseline; width: 100%; background: none; border: 0; padding: 0; text-align: left; color: var(--ink); font: 600 0.95rem/1.35 var(--sans); cursor: pointer; }
.code { font: 700 0.72rem ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--ink); color: var(--paper); border-radius: 5px; padding: 1px 6px; flex: none; }
.meta { margin: 4px 0 8px; }
.detail { border-top: 1px solid var(--line); padding-top: 8px; margin-bottom: 8px; }
.content { white-space: pre-line; font-size: 0.92rem; }
.edit { margin-top: 8px; }
.status { padding: 5px 8px; font-size: 0.85rem; }
.closed { margin-top: 32px; }
.closed select { width: auto; padding: 5px 8px; }
</style>
