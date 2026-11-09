<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import { ROLE_LABELS, auth } from '../auth'
import { formatDate } from '../format'

const users = ref([])
const error = ref('')

const pending = computed(() => users.value.filter((u) => u.status === 'pending'))
const approved = computed(() => users.value.filter((u) => u.status === 'approved'))

async function load() {
  users.value = await api('/users')
}
onMounted(load)

async function update(user, body) {
  error.value = ''
  try {
    await api(`/users/${user.id}`, { method: 'PATCH', body })
  } catch (e) {
    error.value = e.message
  }
  await load()
}

async function remove(user, verb = 'verwijderen') {
  if (!confirm(`Account van ${user.name} (${user.email}) ${verb}? Dit kan niet ongedaan worden gemaakt.`)) return
  error.value = ''
  try {
    await api(`/users/${user.id}`, { method: 'DELETE' })
  } catch (e) {
    error.value = e.message
  }
  await load()
}
</script>

<template>
  <div class="wrap page">
    <span class="eyebrow">Beheer</span>
    <h1>Accounts</h1>
    <p class="lead">Keur nieuwe aanmeldingen goed en bepaal wie wat mag.</p>

    <dl class="roles">
      <div><dt><span class="badge">Lid</span></dt><dd>Mag inloggen en kijken. Kan niks bewerken en ziet de ledenadministratie niet.</dd></div>
      <div><dt><span class="badge signal">Editor</span></dt><dd>Mag columns schrijven, aanpassen en verwijderen, en de teller bijwerken.</dd></div>
      <div><dt><span class="badge alarm">Admin</span></dt><dd>Alle rechten: accounts, rollen en de ledenadministratie.</dd></div>
    </dl>

    <div v-if="error" class="notice error">{{ error }}</div>

    <section class="block">
      <h2>Wachten op goedkeuring <span class="count">{{ pending.length }}</span></h2>
      <p v-if="!pending.length" class="muted">Geen nieuwe aanmeldingen.</p>
      <div v-for="u in pending" :key="u.id" class="card pending">
        <div>
          <strong>{{ u.name }}</strong>
          <div class="small muted">{{ u.email }} · aangemeld {{ formatDate(u.created_at, true) }}</div>
        </div>
        <div class="row">
          <button class="btn sm signal" @click="update(u, { status: 'approved' })">Goedkeuren</button>
          <button class="btn sm danger" @click="remove(u, 'afwijzen en verwijderen')">Afwijzen</button>
        </div>
      </div>
    </section>

    <section class="block">
      <h2>Actieve accounts <span class="count">{{ approved.length }}</span></h2>
      <div class="card table-scroll">
        <table>
          <thead>
            <tr><th>Naam</th><th>E-mail</th><th>Rol</th><th>Laatst ingelogd</th><th /></tr>
          </thead>
          <tbody>
            <tr v-for="u in approved" :key="u.id">
              <td><strong>{{ u.name }}</strong> <span v-if="u.id === auth.user.id" class="muted small">(jij)</span></td>
              <td class="small">{{ u.email }}</td>
              <td>
                <select :value="u.role" :aria-label="`Rol van ${u.name}`" @change="update(u, { role: $event.target.value })">
                  <option v-for="(label, role) in ROLE_LABELS" :key="role" :value="role">{{ label }}</option>
                </select>
              </td>
              <td class="small muted">{{ u.last_login_at ? formatDate(u.last_login_at, true) : 'Nog nooit' }}</td>
              <td class="actions">
                <template v-if="u.id !== auth.user.id">
                  <button class="btn sm ghost" @click="update(u, { status: 'pending' })">Blokkeren</button>
                  <button class="btn sm danger" @click="remove(u)">Verwijderen</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.roles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 24px 0 32px; }
.roles div { border-left: 3px solid var(--line); padding-left: 12px; }
.roles dd { margin: 6px 0 0; color: var(--ink-soft); font-size: 0.9rem; }
.block { margin-bottom: 36px; }
.count { font-family: var(--sans); font-size: 0.9rem; background: var(--line); border-radius: 999px; padding: 2px 10px; vertical-align: middle; }
.pending { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; padding: 16px 20px; }
select { width: auto; padding: 6px 10px; }
.actions { white-space: nowrap; text-align: right; }
.actions .btn + .btn { margin-left: 6px; }
</style>
