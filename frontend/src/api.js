export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

function messageFrom(status, body) {
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    // Validatiefouten van FastAPI omzetten naar iets leesbaars.
    const fields = { email: 'E-mailadres', password: 'Wachtwoord', new_password: 'Nieuw wachtwoord', name: 'Naam', title: 'Titel', body: 'Tekst', author_name: 'Auteur' }
    return detail
      .map((d) => {
        const field = fields[d.loc?.at(-1)] || d.loc?.at(-1)
        if (d.type === 'string_too_short') return `${field} is te kort (minimaal ${d.ctx?.min_length} tekens).`
        if (d.type === 'value_error' && field === 'E-mailadres') return 'Vul een geldig e-mailadres in.'
        return `${field}: ${d.msg}`
      })
      .join(' ')
  }
  return `Er ging iets mis (${status}).`
}

export async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(`/api${path}`, {
    method,
    credentials: 'same-origin',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(res.status, messageFrom(res.status, data))
  return data
}
