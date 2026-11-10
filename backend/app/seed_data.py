"""Startinhoud: leden en de teller. Columns worden via de site toegevoegd."""

from datetime import date

# (naam, bijnaam, functie, dienstdag 0=ma..6=zo, lid sinds)
MEMBERS = [
    ("Robin", "Ragbin", "Voorzitter", 0, None),
    ("Gijs", None, None, 1, None),
    ("Tygo", None, None, 2, None),
    ("Fien", "Foen de bier", None, 3, date(2026, 10, 9)),
    ("Vincent", None, None, 4, None),
    ("Joffry", "Joffert", None, 5, None),
    ("Erik", None, None, 6, None),
    ("Sammi", None, None, None, date(2026, 10, 12)),
]

COUNTER = {
    "last_incident_date": date(2026, 10, 6),
    "last_incident_text": "Tram ontspoord na aanrijding met bestelbus, Van Baerlestraat (Amsterdam)",
    "sticker_count": 2,
}
