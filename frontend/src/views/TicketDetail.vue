<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../auth'
import { formatDate } from '../format'
import { CLOSED, KIND_LABELS, PRIORITY_LABELS, STATUS_LABELS } from '../tickets'

const props = defineProps({ id: String })
const router = useRouter()
const isAdmin = auth.can('admin')

const ticket = ref(null)
const admins = ref([])
const reply = ref({ body: '', internal: false })
const error = ref('')
const busy = ref(false)

const isClosed = computed(() => ticket.value && CLOSED.includes(ticket.value.status))

watch(() => props.id, async (id) => {
  error.value = ''
  try {
    ticket.value = await api(`/tickets/${id}`)
    document.title = `#${ticket.value.id} ${ticket.value.title} · Trauma Tram Tellers`
    if (isAdmin && !admins.value.length) {
      admins.value = (await api('/users')).filter((u) => u.role === 'admin' && u.status === 'approved')
    }
  } catch (e) {
    error.value = e.message
  }
}, { immediate: true })

async function send(extra = {}) {
  error.value = ''
  busy.value = true
  try {
    ticket.value = await api(`/tickets/${props.id}/messages`, { method: 'POST', body: { ...reply.value, ...extra } })
    reply.value = { body: '', internal: false }
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}

async function update(body) {
  error.value = ''
  try {
    ticket.value = await api(`/tickets/${props.id}`, { method: 'PATCH', body })
  } catch (e) {
    error.value = e.message
  }
}

// Antwoorden en meteen de status zetten, zoals in een helpdesk.
async function replyAndSet(status) {
  if (reply.value.body.trim()) await send()
  if (!error.value) await update({ status })
}

async function remove() {
  if (!confirm(`Melding #${ticket.value.id} definitief verwijderen? Gebruik dit alleen voor spam of dubbele meldingen.`)) return
  await api(`/tickets/${props.id}`, { method: 'DELETE' })
  router.push('/meldingen')
}
</script>

<template>
  <div class="wrap page">
    <RouterLink to="/meldingen" class="back small">← Alle meldingen</RouterLink>
    <div v-if="error" class="notice error">{{ error }}</div>

    <div v-if="ticket" class="layout">
      <article>
        <div class="row tags">
          <span class="badge">#{{ ticket.id }}</span>
          <span class="badge" :class="`kind-${ticket.kind}`">{{ KIND_LABELS[ticket.kind] }}</span>
          <span class="badge" :class="`st-${ticket.status}`">{{ STATUS_LABELS[ticket.status] }}</span>
        </div>
        <h1>{{ ticket.title }}</h1>
        <p class="small muted">
          Gemeld door {{ ticket.reporter?.name || 'een verwijderd account' }} op {{ formatDate(ticket.created_at, true) }}
          <template v-if="ticket.page"> · pagina <RouterLink :to="ticket.page">{{ ticket.page }}</RouterLink></template>
        </p>
        <div class="card description">{{ ticket.description }}</div>

        <ol class="timeline">
          <li v-for="m in ticket.messages" :key="m.id" :class="[m.kind, { internal: m.internal, admin: m.from_admin }]">
            <template v-if="m.kind === 'event'">
              <span class="small muted">{{ m.body }} · {{ m.author?.name }} · {{ formatDate(m.created_at, true) }}</span>
            </template>
            <div v-else class="bubble">
              <div class="small meta">
                <strong>{{ m.author?.name || 'Verwijderd account' }}</strong>
                <span v-if="m.from_admin" class="badge">Admin</span>
                <span v-if="m.internal" class="badge internal-badge">Interne notitie</span>
                <span class="muted">{{ formatDate(m.created_at, true) }}</span>
              </div>
              <p>{{ m.body }}</p>
            </div>
          </li>
        </ol>

        <form v-if="ticket.can_reply" class="card reply" @submit.prevent="send()">
          <label class="field">
            <span>{{ isAdmin ? 'Antwoord' : 'Reageren' }}</span>
            <textarea v-model="reply.body" rows="4" maxlength="5000" required :placeholder="isAdmin ? '' : 'Aanvulling of vraag…'" />
          </label>
          <label v-if="isAdmin" class="row check small">
            <input v-model="reply.internal" type="checkbox" /> Interne notitie (niet zichtbaar voor de melder)
          </label>
          <p v-if="!isAdmin && ticket.status === 'opgelost'" class="small muted">Is het toch niet opgelost? Reageer, dan gaat de melding weer open.</p>
          <div class="row">
            <button class="btn signal" :disabled="busy || !reply.body.trim()">{{ reply.internal ? 'Notitie opslaan' : 'Versturen' }}</button>
            <button v-if="isAdmin && !isClosed && !reply.internal" type="button" class="btn ghost" :disabled="busy" @click="replyAndSet('opgelost')">
              {{ reply.body.trim() ? 'Versturen en oplossen' : 'Markeer als opgelost' }}
            </button>
          </div>
        </form>
        <p v-else class="card muted small">Deze melding is gesloten. Is er iets nieuws? Doe dan een nieuwe melding met de knop rechtsonder.</p>
      </article>

      <aside v-if="isAdmin" class="card admin">
        <h3>Behandelen</h3>
        <label class="field">
          <span>Status</span>
          <select :value="ticket.status" @change="update({ status: $event.target.value })">
            <option v-for="(label, s) in STATUS_LABELS" :key="s" :value="s">{{ label }}</option>
          </select>
        </label>
        <label class="field">
          <span>Prioriteit</span>
          <select :value="ticket.priority" @change="update({ priority: $event.target.value })">
            <option v-for="(label, p) in PRIORITY_LABELS" :key="p" :value="p">{{ label }}</option>
          </select>
        </label>
        <label class="field">
          <span>Behandelaar</span>
          <select :value="ticket.assignee?.id ?? ''" @change="$event.target.value ? update({ assignee_id: Number($event.target.value) }) : update({ unassign: true })">
            <option value="">Niemand</option>
            <option v-for="a in admins" :key="a.id" :value="a.id">{{ a.name }}</option>
          </select>
        </label>
        <button v-if="ticket.assignee?.id !== auth.user.id" class="btn sm ghost" @click="update({ assignee_id: auth.user.id, status: ticket.status === 'open' ? 'in_behandeling' : undefined })">Ik pak dit op</button>
        <hr />
        <button class="btn sm danger" @click="remove">Verwijderen</button>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 16px; text-decoration: none; color: var(--muted); }
.layout { display: grid; grid-template-columns: minmax(0, 1fr) 260px; gap: 24px; align-items: start; }
@media (max-width: 860px) { .layout { grid-template-columns: 1fr; } .admin { order: -1; } }
.tags { gap: 6px; }
h1 { margin-top: 12px; font-size: clamp(2rem, 5vw, 3rem); overflow-wrap: anywhere; }
.description { white-space: pre-line; overflow-wrap: anywhere; }
.timeline { list-style: none; padding: 0; margin: 24px 0; display: grid; gap: 12px; }
.timeline li.event { padding-left: 14px; border-left: 2px solid var(--line); }
.bubble { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px 16px; }
li.admin .bubble { border-left: 4px solid var(--signal); }
li.internal .bubble { border-style: dashed; background: color-mix(in srgb, var(--signal) 8%, var(--surface)); }
.meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.bubble p { margin: 6px 0 0; white-space: pre-line; overflow-wrap: anywhere; }
.internal-badge { background: var(--ink); color: var(--paper); }
.check { flex-wrap: nowrap; gap: 8px; margin-bottom: 14px; font-weight: 600; }
.admin { position: sticky; top: 88px; }
.admin hr { border: 0; border-top: 1px solid var(--line); margin: 16px 0; }
</style>
