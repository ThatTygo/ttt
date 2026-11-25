<script setup>
import { ref, watch } from 'vue'
import { api } from '../api'
import { formatDate } from '../format'
import LikeButton from './LikeButton.vue'

const props = defineProps({ columnId: { type: [String, Number], required: true } })

const likes = ref(null)
const comments = ref([])
const draft = ref('')
const editing = ref(null) // { id, body }
const error = ref('')
const sending = ref(false)

async function load() {
  const data = await api(`/columns/${props.columnId}/reactions`)
  likes.value = data.likes
  comments.value = data.comments
}
watch(() => props.columnId, load, { immediate: true })

const initials = (name) => name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('')
const hue = (id) => (id * 67) % 360

async function send() {
  error.value = ''
  sending.value = true
  try {
    comments.value.push(await api(`/columns/${props.columnId}/comments`, { method: 'POST', body: { body: draft.value } }))
    draft.value = ''
  } catch (e) {
    error.value = e.message
  } finally {
    sending.value = false
  }
}

async function saveEdit(c) {
  error.value = ''
  try {
    Object.assign(c, await api(`/comments/${c.id}`, { method: 'PATCH', body: { body: editing.value.body } }))
    editing.value = null
  } catch (e) {
    error.value = e.message
  }
}

async function remove(c) {
  if (!confirm('Deze reactie verwijderen?')) return
  await api(`/comments/${c.id}`, { method: 'DELETE' })
  comments.value = comments.value.filter((x) => x.id !== c.id)
}

// Ctrl/Cmd + Enter verstuurt.
function onKey(event, action) {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) action()
}
</script>

<template>
  <section class="reactions" aria-label="Reacties">
    <div v-if="likes" class="row column-like">
      <LikeButton :path="`/columns/${columnId}/like`" :likes="likes" @update="likes = $event" />
      <span class="small muted">{{ likes.names.length ? likes.names.slice(0, 3).join(', ') + (likes.names.length > 3 ? ` en ${likes.names.length - 3} anderen` : '') : 'Vind je dit een goede column?' }}</span>
    </div>

    <h2>Reacties <span class="count">{{ comments.length }}</span></h2>

    <ol class="list">
      <li v-for="c in comments" :key="c.id" class="comment">
        <span class="initials" :style="{ '--hue': hue(c.author.id) }" aria-hidden="true">{{ initials(c.author.name) }}</span>
        <div class="bubble">
          <div class="meta small">
            <strong>{{ c.author.name }}</strong>
            <span class="muted">{{ formatDate(c.created_at, true) }}<template v-if="c.edited_at"> · bewerkt</template></span>
          </div>
          <form v-if="editing?.id === c.id" @submit.prevent="saveEdit(c)">
            <textarea v-model="editing.body" rows="3" maxlength="2000" required @keydown="onKey($event, () => saveEdit(c))" />
            <div class="row">
              <button class="btn sm signal">Opslaan</button>
              <button type="button" class="btn sm ghost" @click="editing = null">Annuleren</button>
            </div>
          </form>
          <p v-else class="text">{{ c.body }}</p>
          <div class="row actions">
            <LikeButton small :path="`/comments/${c.id}/like`" :likes="c.likes" @update="c.likes = $event" />
            <button v-if="c.can_edit && editing?.id !== c.id" class="linkish" @click="editing = { id: c.id, body: c.body }">Bewerken</button>
            <button v-if="c.can_delete" class="linkish" @click="remove(c)">Verwijderen</button>
          </div>
        </div>
      </li>
    </ol>
    <p v-if="!comments.length" class="muted small">Nog geen reacties. Wees de eerste.</p>

    <form class="new" @submit.prevent="send">
      <div v-if="error" class="notice error">{{ error }}</div>
      <label class="field">
        <span>Jouw reactie</span>
        <textarea v-model="draft" rows="3" maxlength="2000" required placeholder="Houd moed…" @keydown="onKey($event, send)" />
        <small>{{ draft.length }}/2000 · Ctrl+Enter om te plaatsen</small>
      </label>
      <button class="btn signal" :disabled="sending || !draft.trim()">Plaatsen</button>
    </form>
  </section>
</template>

<style scoped>
.reactions { margin-top: 40px; }
.column-like { margin-bottom: 32px; }
h2 { display: flex; align-items: center; gap: 10px; }
.count { font: 700 0.85rem var(--sans); background: var(--line); border-radius: 999px; padding: 2px 10px; }
.list { list-style: none; padding: 0; margin: 0 0 16px; display: grid; gap: 14px; }
.comment { display: flex; gap: 12px; align-items: flex-start; }
.initials {
  flex: none; width: 36px; height: 36px; border-radius: 50%;
  display: grid; place-items: center; padding-top: 0.1em;
  font-family: var(--display); font-size: 0.95rem; letter-spacing: 0.04em;
  color: #fff; background: hsl(var(--hue) 45% 38%);
}
.bubble { flex: 1; min-width: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 10px 14px; }
.meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: baseline; }
.text { margin: 4px 0 8px; white-space: pre-line; overflow-wrap: anywhere; }
.actions { gap: 14px; }
.linkish { background: none; border: 0; padding: 0; font: 600 0.8rem var(--sans); color: var(--muted); cursor: pointer; }
.linkish:hover { color: var(--ink); }
.new { margin-top: 20px; }
textarea { min-height: 0; }
</style>
