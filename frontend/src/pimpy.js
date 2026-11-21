export const STATUS_LABELS = {
  new: 'Nieuw',
  started: 'Bezig',
  done: 'Klaar',
  not_done: 'Niet gedaan',
  finished: 'Afgerond',
  deleted: 'Vervallen',
}

// Kolommen op het takenbord; afgerond/vervallen staan apart.
export const OPEN_STATUSES = ['new', 'started', 'done', 'not_done']
export const CLOSED_STATUSES = ['finished', 'deleted']

export const SYNTAX_HELP = [
  ['ACTIE Robin, Gijs: stickers bestellen', 'Eén taak voor Robin en Gijs samen'],
  ['ACTIES Robin, Gijs: notulen lezen', 'Een aparte taak voor elk van hen'],
  ['ACTIE: domein verlengen', 'Zonder namen: de hele groep'],
  ['DONE 1A, 2B', 'Taken met deze codes zijn afgerond'],
  ['REMOVE 3C', 'Taken met deze codes vervallen'],
  ['MEETING 26-11-2026 13:30(2) Vergadering', 'Vergadering op de agenda (duur in uren, standaard 1)'],
]
