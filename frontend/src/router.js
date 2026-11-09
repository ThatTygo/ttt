import { createRouter, createWebHistory } from 'vue-router'
import { auth } from './auth'

const routes = [
  { path: '/', component: () => import('./views/Home.vue') },
  { path: '/over-ons', component: () => import('./views/About.vue'), meta: { title: 'Over ons' } },
  { path: '/privacy', component: () => import('./views/Privacy.vue'), meta: { title: 'Privacybeleid' } },
  { path: '/columns', component: () => import('./views/Columns.vue'), meta: { title: 'Columns' } },
  { path: '/columns/nieuw', component: () => import('./views/ColumnEditor.vue'), meta: { role: 'editor', title: 'Nieuwe column' } },
  { path: '/columns/:id(\\d+)', component: () => import('./views/ColumnDetail.vue'), props: true },
  { path: '/columns/:id(\\d+)/bewerken', component: () => import('./views/ColumnEditor.vue'), props: true, meta: { role: 'editor', title: 'Column bewerken' } },
  { path: '/rooster', component: () => import('./views/Roster.vue'), meta: { role: 'editor', title: 'Dienstrooster' } },
  { path: '/leden', component: () => import('./views/Members.vue'), meta: { role: 'admin', title: 'Leden' } },
  { path: '/beheer/accounts', component: () => import('./views/AdminUsers.vue'), meta: { role: 'admin', title: 'Accounts' } },
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
