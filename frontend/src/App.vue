<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ReportButton from './components/ReportButton.vue'
import TramLogo from './components/TramLogo.vue'
import UserAvatar from './components/UserAvatar.vue'
import { api } from './api'
import { WIKI_URL, auth } from './auth'

const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)
const openTickets = ref(0)

// Admins zien in het menu hoeveel nieuwe meldingen er zijn.
async function countTickets() {
  openTickets.value = auth.can('admin') ? (await api('/tickets/open-count').catch(() => ({ count: 0 }))).count : 0
}
watch(() => route.fullPath, () => {
  menuOpen.value = false
  countTickets()
}, { immediate: true })

async function logout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <a class="skip" href="#inhoud">Naar inhoud</a>
  <header class="site-header">
    <div class="wrap bar">
      <RouterLink to="/" class="brand">
        <TramLogo />
        <span class="brand-text">Trauma Tram Tellers</span>
      </RouterLink>

      <button class="menu-toggle" :aria-expanded="menuOpen" aria-controls="hoofdmenu" @click="menuOpen = !menuOpen">
        {{ menuOpen ? 'Sluit' : 'Menu' }}
      </button>

      <nav id="hoofdmenu" :class="{ open: menuOpen }">
        <RouterLink v-if="auth.user" to="/columns">Columns</RouterLink>
        <RouterLink v-if="auth.user" to="/profielen">Wie is wie</RouterLink>
        <RouterLink to="/over-ons">Over ons</RouterLink>
        <RouterLink v-if="auth.can('editor')" to="/pimpy">Pimpy</RouterLink>
        <a v-if="auth.can('editor')" :href="WIKI_URL">Wiki</a>
        <RouterLink v-if="auth.can('editor')" to="/rooster">Rooster</RouterLink>
        <RouterLink v-if="auth.can('admin')" to="/leden">Leden</RouterLink>
        <RouterLink v-if="auth.can('admin')" to="/beheer/accounts">Accounts</RouterLink>
        <RouterLink v-if="auth.can('admin')" to="/meldingen">
          Meldingen<span v-if="openTickets" class="count" :aria-label="`${openTickets} nieuw`">{{ openTickets }}</span>
        </RouterLink>
        <span class="divider" />
        <template v-if="auth.user">
          <RouterLink to="/account" class="me" :title="`Mijn account (${auth.user.name})`">
            <UserAvatar :user="auth.user" :size="30" />
            <span>{{ auth.user.name }}</span>
          </RouterLink>
          <button class="linkish" @click="logout">Uitloggen</button>
        </template>
        <template v-else>
          <RouterLink to="/inloggen">Inloggen</RouterLink>
          <RouterLink to="/aanmelden" class="btn signal sm">Word lid</RouterLink>
        </template>
      </nav>
    </div>
  </header>

  <main id="inhoud">
    <RouterView />
  </main>

  <ReportButton v-if="auth.user" />

  <footer class="site-footer">
    <div class="wrap foot">
      <div>
        <strong class="foot-brand">TTT</strong>
        <span class="muted small">De stilte is tijdelijk, de traditie is eeuwig.</span>
      </div>
      <nav class="row small">
        <RouterLink to="/over-ons">Over ons</RouterLink>
        <RouterLink to="/privacy">Privacybeleid</RouterLink>
        <span class="muted">Pas op bij het oversteken.</span>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
.skip { position: absolute; left: -999px; }
.skip:focus { left: 16px; top: 16px; z-index: 10; background: var(--signal); color: var(--signal-ink); padding: 8px 12px; border-radius: 8px; }

.site-header {
  position: sticky;
  top: 0;
  z-index: 5;
  background: color-mix(in srgb, var(--paper) 88%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.bar { display: flex; align-items: center; gap: 16px; min-height: 68px; }
.brand { display: flex; align-items: center; gap: 10px; text-decoration: none; margin-right: auto; }
.brand-text { font-family: var(--display); font-size: 1.6rem; letter-spacing: 0.04em; line-height: 1; padding-top: 3px; }

nav#hoofdmenu { display: flex; align-items: center; gap: 22px; font-weight: 600; font-size: 0.95rem; }
nav#hoofdmenu a:not(.btn) { white-space: nowrap; text-decoration: none; padding: 4px 0; border-bottom: 2px solid transparent; }
nav#hoofdmenu a:not(.btn):hover, nav#hoofdmenu a.router-link-active { border-bottom-color: var(--signal); }
.count { margin-left: 6px; display: inline-block; min-width: 20px; padding: 0 6px; border-radius: 999px; background: var(--alarm); color: #fff; font-size: 0.72rem; line-height: 20px; text-align: center; }
.divider { width: 1px; height: 22px; background: var(--line); }
.me { display: inline-flex; align-items: center; gap: 8px; }
.me span { max-width: 14ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.linkish { background: none; border: 0; padding: 0; font: inherit; color: var(--muted); cursor: pointer; }
.linkish:hover { color: var(--ink); }

.menu-toggle { display: none; background: none; border: 1.5px solid var(--line); color: var(--ink); border-radius: 999px; padding: 6px 14px; font: 600 0.9rem var(--sans); cursor: pointer; }

@media (max-width: 1080px) {
  .menu-toggle { display: block; }
  nav#hoofdmenu {
    display: none;
    position: absolute;
    top: 68px;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
    padding: 12px 16px 20px;
    background: var(--paper);
    border-bottom: 1px solid var(--line);
  }
  nav#hoofdmenu.open { display: flex; }
  nav#hoofdmenu a:not(.btn) { padding: 10px 0; }
  .divider { width: 100%; height: 1px; margin: 6px 0; }
  .linkish { text-align: left; padding: 10px 0; }
}

.site-footer { border-top: 1px solid var(--line); padding: 28px 0 40px; }
.foot { display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; align-items: center; }
.foot-brand { font-family: var(--display); font-size: 1.5rem; letter-spacing: 0.06em; margin-right: 10px; font-weight: 400; }
.foot a { text-decoration: none; }
.foot a:hover { text-decoration: underline; }
</style>
