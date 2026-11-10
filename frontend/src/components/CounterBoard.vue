<script setup>
import { computed, ref } from 'vue'
import { api } from '../api'
import { auth } from '../auth'
import { daysSince, formatDate } from '../format'

const props = defineProps({ counter: Object })
const emit = defineEmits(['updated'])

const days = computed(() => daysSince(props.counter?.last_incident_date))
const digits = computed(() => (days.value == null ? ['–', '–', '–'] : String(days.value).padStart(3, '0').split('')))

const editing = ref(false)
const form = ref({})
const error = ref('')

function startEdit() {
  form.value = { ...props.counter }
  error.value = ''
  editing.value = true
}

async function save() {
  try {
    const updated = await api('/counter', {
      method: 'PUT',
      body: {
        last_incident_date: form.value.last_incident_date || null,
        last_incident_text: form.value.last_incident_text || null,
        sticker_count: Number(form.value.sticker_count) || 0,
      },
    })
    emit('updated', updated)
    editing.value = false
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <section class="board" aria-label="De teller">
    <div class="board-head">
      <span class="lamp" />
      <span>Dagen sinds het laatste stickerwaardige tramincident</span>
    </div>

    <div class="flaps" :aria-label="days == null ? 'Nog geen incident gelogd' : `${days} dagen`">
      <span v-for="(d, i) in digits" :key="i" class="flap" :style="{ animationDelay: `${i * 90}ms` }">{{ d }}</span>
    </div>

    <dl class="stats">
      <div>
        <dt>Stickers op de muur</dt>
        <dd>{{ counter?.sticker_count ?? '–' }}</dd>
      </div>
      <div>
        <dt>Laatste incident</dt>
        <dd>{{ formatDate(counter?.last_incident_date) }}</dd>
      </div>
    </dl>
    <p v-if="counter?.last_incident_text" class="last">{{ counter.last_incident_text }}</p>

    <template v-if="auth.can('editor')">
      <button v-if="!editing" class="edit-link" @click="startEdit">Teller bijwerken</button>
      <form v-else class="edit" @submit.prevent="save">
        <div v-if="error" class="notice error">{{ error }}</div>
        <label class="field"><span>Datum laatste incident</span><input v-model="form.last_incident_date" type="date" /></label>
        <label class="field"><span>Omschrijving</span><input v-model="form.last_incident_text" maxlength="300" /></label>
        <label class="field"><span>Aantal stickers</span><input v-model="form.sticker_count" type="number" min="0" /></label>
        <div class="row">
          <button class="btn signal sm">Opslaan</button>
          <button type="button" class="btn ghost sm" @click="editing = false">Annuleren</button>
        </div>
      </form>
    </template>
  </section>
</template>

<style scoped>
.board {
  --b-ink: var(--board-ink);
  background: var(--board);
  color: #e9edf3;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 24px 48px -24px rgba(6, 11, 20, 0.7), inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}
.board-head { display: flex; align-items: center; gap: 10px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #9aa6b8; }
.lamp { width: 9px; height: 9px; border-radius: 50%; background: var(--alarm); box-shadow: 0 0 12px var(--alarm); animation: blink 1.6s infinite; }
@keyframes blink { 50% { opacity: 0.25; } }

.flaps { display: flex; gap: 8px; margin: 20px 0 22px; }
.flap {
  position: relative;
  flex: 1;
  max-width: 96px;
  aspect-ratio: 3 / 4;
  display: grid;
  place-items: center;
  font-family: var(--display);
  font-size: clamp(3.6rem, 10vw, 5.6rem);
  line-height: 1;
  padding-top: 0.08em;
  color: var(--b-ink);
  background: linear-gradient(#1b2639 50%, #151f30 50%);
  border-radius: 10px;
  box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.35);
  animation: flip 0.5s cubic-bezier(0.3, 1.4, 0.5, 1) both;
}
.flap::after { content: ''; position: absolute; left: 0; right: 0; top: 50%; height: 2px; background: #060b14; }
@keyframes flip { from { transform: rotateX(80deg); opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .flap, .lamp { animation: none; } }

.stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 0; }
.stats div { background: rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 10px 14px; }
dt { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: #9aa6b8; }
dd { margin: 2px 0 0; font-family: var(--display); font-size: 1.7rem; letter-spacing: 0.03em; color: #fff; }
.last { margin: 14px 0 0; font-size: 0.9rem; color: #b8c2d1; }

.edit-link { margin-top: 14px; background: none; border: 0; padding: 0; color: var(--b-ink); font: 600 0.85rem var(--sans); cursor: pointer; text-decoration: underline; text-underline-offset: 3px; }
.edit { margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.1); }
.edit .field > span { color: #b8c2d1; }
.edit input { background: #0a111e; border-color: #26324a; color: #fff; }
.edit .btn.ghost { color: #e9edf3; border-color: #3a4862; }
</style>
