import { createRouter, createWebHistory } from 'vue-router'
import { auth } from './auth'

const routes = [
  { path: '/', component: () => import('./views/Home.vue') },
  { path: '/over-ons', component: () => import('./views/About.vue'), meta: { title: 'Over ons' } },
  { path: '/privacy', component: () => import('./views/Privacy.vue'), meta: { title: 'Privacybeleid' } },
  { path: '/columns', component: () => import('./views/Columns.vue'), meta: { role: 'user', title: 'Columns' } },
  { path: '/columns/nieuw', component: () => import('./views/ColumnEditor.vue'), meta: { role: 'editor', title: 'Nieuwe column' } },
  { path: '/columns/:id(\\d+)', component: () => import('./views/ColumnDetail.vue'), props: true, meta: { role: 'user' } },
  { path: '/columns/:id(\\d+)/bewerken', component: () => import('./views/ColumnEditor.vue'), props: true, meta: { role: 'editor', title: 'Column bewerken' } },
  { path: '/rooster', component: () => import('./views/Roster.vue'), meta: { role: 'editor', title: 'Dienstrooster' } },
  {
    path: '/pimpy',
    component: () => import('./views/pimpy/PimpyLayout.vue'),
    meta: { role: 'editor', title: 'Pimpy' },
    children: [
      { path: '', redirect: '/pimpy/taken' },
      { path: 'taken', component: () => import('./views/pimpy/Tasks.vue'), meta: { title: 'Taken' } },
      { path: 'notulen', component: () => import('./views/pimpy/Minutes.vue'), meta: { title: 'Notulen' } },
      { path: 'notulen/nieuw', component: () => import('./views/pimpy/MinuteEditor.vue'), meta: { title: 'Notulen toevoegen' } },
      { path: 'notulen/:id(\\d+)', component: () => import('./views/pimpy/MinuteDetail.vue'), props: true, meta: { title: 'Notulen' } },
      { path: 'agenda', component: () => import('./views/pimpy/Agenda.vue'), meta: { title: 'Agenda' } },
      { path: 'groepen', component: () => import('./views/pimpy/Groups.vue'), meta: { role: 'admin', title: 'Groepen' } },
    ],
  },
  { path: '/leden', component: () => import('./views/Members.vue'), meta: { role: 'admin', title: 'Leden' } },
  { path: '/beheer/accounts', component: () => import('./views/AdminUsers.vue'), meta: { role: 'admin', title: 'Accounts' } },
  { path: '/profielen', component: () => import('./views/Profiles.vue'), meta: { role: 'user', title: 'Wie is wie' } },
  { path: '/profiel/:id(\\d+)', component: () => import('./views/Profile.vue'), props: true, meta: { role: 'user', title: 'Profiel' } },
  { path: '/meldingen', component: () => import('./views/Tickets.vue'), meta: { role: 'user', title: 'Meldingen' } },
  { path: '/meldingen/:id(\\d+)', component: () => import('./views/TicketDetail.vue'), props: true, meta: { role: 'user', title: 'Melding' } },
  { path: '/account', component: () => import('./views/Account.vue'), meta: { role: 'user', title: 'Mijn account' } },
  { path: '/inloggen', component: () => import('./views/Login.vue'), meta: { title: 'Inloggen' } },
  { path: '/aanmelden', component: () => import('./views/Register.vue'), meta: { title: 'Aanmelden' } },
  { path: '/:pathMatch(.*)*', component: () => import('./views/NotFound.vue'), meta: { title: 'Niet gevonden' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})

router.beforeEach((to) => {
  const role = to.meta.role
  if (!role) return true
  if (!auth.user) return { path: '/inloggen', query: { terug: to.fullPath } }
  if (!auth.can(role)) return { path: '/' }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Trauma Tram Tellers` : 'Trauma Tram Tellers'
})

export default router
