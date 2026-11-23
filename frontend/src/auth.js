import { reactive } from 'vue'
import { api } from './api'

const RANK = { user: 0, editor: 1, admin: 2 }

export const auth = reactive({
  user: null,
  loaded: false,

  async load() {
    try {
      this.user = await api('/auth/me')
    } catch {
      this.user = null
    }
    this.loaded = true
  },

  async login(email, password) {
    this.user = await api('/auth/login', { method: 'POST', body: { email, password } })
  },

  async logout() {
    await api('/auth/logout', { method: 'POST' })
    this.user = null
  },

  can(role) {
    return !!this.user && RANK[this.user.role] >= RANK[role]
  },
})

export const ROLE_LABELS = { user: 'Lid', editor: 'Editor', admin: 'Admin' }
export const DAYS = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']

/** Adres van de wiki: wiki.<dit domein>. */
export const WIKI_URL = `${location.protocol}//wiki.${location.host}/`

/** Alleen terugsturen naar de eigen wiki, nooit naar een willekeurige site. */
export function isWikiUrl(value) {
  if (typeof value !== 'string') return false
  try {
    const url = new URL(value)
    return url.protocol === location.protocol && url.host === `wiki.${location.host}`
  } catch {
    return false
  }
}
