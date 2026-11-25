<script setup>
import { ref, watch } from 'vue'
import { api } from '../api'
import { ROLE_LABELS, auth } from '../auth'
import { formatDate } from '../format'
import UserAvatar from '../components/UserAvatar.vue'

const props = defineProps({ id: String })
const profile = ref(null)
const error = ref('')

watch(() => props.id, async (id) => {
  error.value = ''
  profile.value = null
  try {
    profile.value = await api(`/profiles/${id}`)
    document.title = `${profile.value.name} · Trauma Tram Tellers`
  } catch (e) {
    error.value = e.message
  }
}, { immediate: true })
</script>

<template>
  <div class="narrow page">
    <RouterLink to="/profielen" class="back small">← Alle leden</RouterLink>
    <div v-if="error" class="notice error">{{ error }}</div>

    <article v-if="profile" class="card profile">
      <UserAvatar :user="profile" :size="140" />
      <div class="info">
        <span class="badge" :class="{ signal: profile.role !== 'user' }">{{ ROLE_LABELS[profile.role] }}</span>
        <h1>{{ profile.name }}</h1>
        <p class="muted small">Lid sinds {{ formatDate(profile.created_at) }}</p>
        <p v-if="profile.bio" class="bio">{{ profile.bio }}</p>
        <p v-else class="muted">{{ profile.id === auth.user.id ? 'Je hebt nog niks over jezelf geschreven.' : 'Nog geen beschrijving.' }}</p>
        <RouterLink v-if="profile.id === auth.user.id" to="/account" class="btn sm ghost">Profiel bewerken</RouterLink>
      </div>
    </article>
  </div>
</template>

<style scoped>
.back { display: inline-block; margin-bottom: 20px; text-decoration: none; color: var(--muted); }
.profile { display: flex; gap: 28px; align-items: flex-start; padding: 28px; }
@media (max-width: 560px) { .profile { flex-direction: column; align-items: center; text-align: center; } }
.info { min-width: 0; flex: 1; }
h1 { margin-top: 10px; overflow-wrap: anywhere; }
.bio { white-space: pre-line; font-family: var(--serif); font-size: 1.1rem; overflow-wrap: anywhere; }
</style>
