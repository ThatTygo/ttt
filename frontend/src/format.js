const TZ = 'Europe/Amsterdam'

export function formatDate(value, withTime = false) {
  if (!value) return '—'
  const opts = { day: 'numeric', month: 'long', year: 'numeric', timeZone: TZ }
  if (withTime) Object.assign(opts, { hour: '2-digit', minute: '2-digit' })
  return new Intl.DateTimeFormat('nl-NL', opts).format(new Date(value))
}

export function formatShortDate(value) {
  return new Intl.DateTimeFormat('nl-NL', { day: 'numeric', month: 'short', timeZone: TZ }).format(new Date(value))
}

/** Datum als YYYY-MM-DD in Amsterdamse tijd. */
export function amsterdamDay(date = new Date()) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: TZ }).format(date)
}

export function daysSince(isoDay) {
  if (!isoDay) return null
  const ms = Date.parse(amsterdamDay()) - Date.parse(isoDay)
  return Math.max(0, Math.round(ms / 86400000))
}

/** Waarde voor <input type="datetime-local"> in Amsterdamse tijd. */
export function toLocalInput(value) {
  const d = value ? new Date(value) : new Date()
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('en-GB', {
      timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
    }).formatToParts(d).map((p) => [p.type, p.value]),
  )
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}

/** Splitst een columntekst in alinea's (lege regel = nieuwe alinea). */
export function paragraphs(text) {
  return text.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean)
}
