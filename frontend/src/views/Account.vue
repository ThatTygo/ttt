<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { ROLE_LABELS, auth } from '../auth'
import { formatDate } from '../format'

const router = useRouter()
const name = ref(auth.user.name)
const pw = ref({ current: '', next: '' })
const delPw = ref('')
const msg = ref({ kind: '', text: '' })

function flash(kind, text) {
  msg.value = { kind, text }
}

async function saveName() {
  try {
    auth.user = await api('/account', { method: 'PATCH', body: { name: name.value } })
    flash('ok', 'Naam opgeslagen.')
  } catch (e) {
    flash('error', e.message)
  }
}

async function savePassword() {
  try {
    await api('/account', { method: 'PATCH', body: { current_password: pw.value.current, new_password: pw.value.next } })
    pw.value = { current: '', next: '' }
    flash('ok', 'Wachtwoord gewijzigd.')
  } catch (e) {
    flash('error', e.message)
  }
}

async function exportData() {
  const data = await api('/account/export')
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'ttt-mijn-gegevens.json' })
  a.click()
  URL.revokeObjectURL(a.href)
}

async function deleteAccount() {
  if (!confirm('Weet je zeker dat je je account wilt verwijderen? Dit kan niet ongedaan worden gemaakt.')) return
  try {
    await api('/account', { method: 'DELETE', body: { password: delPw.value } })
    auth.user = null
    router.push('/')
  } catch (e) {
    flash('error', e.message)
  }
}
</script>

<template>
  <div class="narrow page">
    <span class="eyebrow">{{ ROLE_LABELS[auth.user.role] }} · lid sinds {{ formatDate(auth.user.created_at) }}</span>
    <h1>Mijn account</h1>
    <p class="muted">{{ auth.user.email }}</p>

    <div v-if="msg.text" class="notice" :class="msg.kind">{{ msg.text }}</div>

    <form class="card" @submit.prevent="saveName">
      <h3>Naam</h3>
      <label class="field"><span>Weergavenaam</span><input v-model="name" required minlength="2" maxlength="80" /></label>
      <button class="btn">Opslaan</button>
    </form>

    <form class="card" @submit.prevent="savePassword">
      <h3>Wachtwoord wijzigen</h3>
      <label class="field"><span>Huidig wachtwoord</span><input v-model="pw.current" type="password" autocomplete="current-password" required /></label>
      <label class="field"><span>Nieuw wachtwoord</span><input v-model="pw.next" type="password" autocomplete="new-password" minlength="10" required /><small>Minimaal 10 tekens.</small></label>
      <button class="btn">Wachtwoord wijzigen</button>
    </form>

    <section class="card">
      <h3>Mijn gegevens</h3>
      <p class="muted">Download alles wat we over je account opslaan. Zie ook het <RouterLink to="/privacy">privacybeleid</RouterLink>.</p>
      <button class="btn ghost" @click="exportData">Gegevens downloaden</button>
    </section>

    <form class="card danger-zone" @submit.prevent="deleteAccount">
      <h3>Account verwijderen</h3>
      <p class="muted">Je account en sessies worden direct gewist. Columns die je schreef blijven staan onder je naam; vraag een admin als je die ook weg wilt.</p>
      <label class="field"><span>Bevestig met je wachtwoord</span><input v-model="delPw" type="password" autocomplete="current-password" required /></label>
      <button class="btn danger">Account verwijderen</button>
    </form>
  </div>
</template>

<style scoped>
.card { margin-bottom: 16px; }
.danger-zone { border-color: color-mix(in srgb, var(--alarm) 40%, var(--line)); }
</style>
