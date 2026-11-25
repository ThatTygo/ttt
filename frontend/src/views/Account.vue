<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { ROLE_LABELS, auth } from '../auth'
import { formatDate } from '../format'
import UserAvatar from '../components/UserAvatar.vue'

const router = useRouter()
const name = ref(auth.user.name)
const bio = ref(auth.user.bio || '')
const uploading = ref(false)
const fileInput = ref(null)
const pw = ref({ current: '', next: '' })
const delPw = ref('')
const emailTasks = ref(auth.user.email_tasks)
const msg = ref({ kind: '', text: '' })

function flash(kind, text) {
  msg.value = { kind, text }
}

async function saveProfile() {
  try {
    auth.user = await api('/account', { method: 'PATCH', body: { name: name.value, bio: bio.value } })
    flash('ok', 'Profiel opgeslagen.')
  } catch (e) {
    flash('error', e.message)
  }
}

async function uploadAvatar(event) {
  const file = event.target.files[0]
  event.target.value = ''
  if (!file) return
  if (file.size > 8 * 1024 * 1024) return flash('error', 'De foto is te groot (maximaal 8 MB).')
  uploading.value = true
  try {
    auth.user = await api('/account/avatar', { method: 'PUT', body: file })
    flash('ok', 'Profielfoto opgeslagen.')
  } catch (e) {
    flash('error', e.message)
  } finally {
    uploading.value = false
  }
}

async function removeAvatar() {
  if (!confirm('Je profielfoto verwijderen?')) return
  try {
    auth.user = await api('/account/avatar', { method: 'DELETE' })
    flash('ok', 'Profielfoto verwijderd.')
  } catch (e) {
    flash('error', e.message)
  }
}

async function saveEmailTasks() {
  try {
    auth.user = await api('/account', { method: 'PATCH', body: { email_tasks: emailTasks.value } })
    flash('ok', emailTasks.value ? 'Je krijgt weer mail bij nieuwe taken.' : 'Je krijgt geen mail meer bij nieuwe taken.')
  } catch (e) {
    emailTasks.value = !emailTasks.value
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
    <p class="muted">{{ auth.user.email }} · <RouterLink :to="`/profiel/${auth.user.id}`">Bekijk je profiel</RouterLink></p>

    <div v-if="msg.text" class="notice" :class="msg.kind">{{ msg.text }}</div>

    <section class="card">
      <h3>Profielfoto</h3>
      <div class="row photo">
        <UserAvatar :user="auth.user" :size="96" />
        <div class="row">
          <button type="button" class="btn sm" :disabled="uploading" @click="fileInput.click()">
            {{ uploading ? 'Bezig met uploaden…' : auth.user.avatar_url ? 'Andere foto kiezen' : 'Foto kiezen' }}
          </button>
          <button v-if="auth.user.avatar_url" type="button" class="btn sm ghost" @click="removeAvatar">Verwijderen</button>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp,image/gif" hidden @change="uploadAvatar" />
        </div>
      </div>
      <small class="muted">JPG, PNG, WebP of GIF, maximaal 8 MB. De foto wordt vierkant bijgesneden; locatiegegevens in de foto worden verwijderd.</small>
    </section>

    <form class="card" @submit.prevent="saveProfile">
      <h3>Profiel</h3>
      <label class="field"><span>Weergavenaam</span><input v-model="name" required minlength="2" maxlength="80" /></label>
      <label class="field">
        <span>Over jezelf</span>
        <textarea v-model="bio" rows="4" maxlength="500" placeholder="Bijv. favoriete tramlijn, dagdienst, of je beste tramtrauma." />
        <small>{{ bio.length }}/500 · zichtbaar voor alle ingelogde leden</small>
      </label>
      <button class="btn">Opslaan</button>
    </form>

    <section v-if="auth.can('editor')" class="card">
      <h3>E-mail</h3>
      <label class="row check">
        <input v-model="emailTasks" type="checkbox" @change="saveEmailTasks" />
        <span>Stuur me een mail als ik in Pimpy een nieuwe taak krijg</span>
      </label>
    </section>

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
.photo { gap: 20px; margin-bottom: 10px; }
.check { flex-wrap: nowrap; gap: 10px; font-weight: 600; }
.danger-zone { border-color: color-mix(in srgb, var(--alarm) 40%, var(--line)); }
</style>
