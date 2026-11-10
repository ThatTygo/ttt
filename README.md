# Trauma Tram Tellers

Website van de TTT: intro, over ons, privacybeleid, columns en een afgeschermde ledenadministratie.

- **Frontend:** Vue 3 + Vite (`frontend/`)
- **Backend:** Python, FastAPI + SQLAlchemy (`backend/`)
- **Database:** PostgreSQL
- **Productie:** Docker Compose met Caddy (automatisch HTTPS via Let's Encrypt)

## Rollen

| Rol | Mag |
| --- | --- |
| *bezoeker* | Home, columns, over ons, privacy lezen |
| `user` | inloggen, eigen account beheren |
| `editor` | + columns schrijven/bewerken/verwijderen, teller bijwerken, dienstrooster bekijken |
| `admin` | + accounts goedkeuren, rollen wijzigen, ledenadministratie bekijken en beheren |

Nieuwe accounts krijgen de rol `user` met status *pending* en kunnen pas inloggen nadat een admin ze heeft goedgekeurd (menu **Accounts**).

## Live zetten

Strato-webhosting draait geen Python of PostgreSQL, dus je hebt een (kleine) VPS nodig, bijv. een Strato VPS of een andere Linux-server in de EU. Het domein blijft gewoon bij Strato.

1. **Server:** installeer Docker (`curl -fsSL https://get.docker.com | sh`) en zet deze repo erop.
2. **DNS bij Strato:** maak een A-record voor `@` en `www` naar het IP-adres van de server (en AAAA bij IPv6).
3. **Config:**
   ```bash
   cp .env.example .env
   # vul DOMAIN en POSTGRES_PASSWORD in
   ```
4. **Starten:**
   ```bash
   docker compose up -d --build
   ```
   Bij de eerste start worden de tabellen aangemaakt. De database is dan leeg: geen accounts, leden of columns.
5. **Eerste admin aanmaken:**
   ```bash
   docker compose exec api python -m app.cli create-admin jouw@email.nl Jouw Naam
   ```
6. Pas `frontend/src/site.js` aan (contactadres voor het privacybeleid, hostingpartij) en bouw opnieuw.

Updaten: `git pull && docker compose up -d --build`.

Back-up van de database:
```bash
docker compose exec db pg_dump -U ttt ttt > backup.sql
```

## Lokaal ontwikkelen

```bash
# Database
docker run -d --name ttt-dev-db -e POSTGRES_USER=ttt -e POSTGRES_PASSWORD=ttt -e POSTGRES_DB=ttt -p 127.0.0.1:55432:5432 postgres:17-alpine

# Backend
cd backend
uv venv && uv pip install -r requirements.txt
printf 'DATABASE_URL=postgresql+psycopg://ttt:ttt@localhost:55432/ttt\nCOOKIE_SECURE=false\n' > .env
.venv/bin/python -m app.cli init-db
.venv/bin/python -m app.cli create-admin admin@example.com Admin
.venv/bin/uvicorn app.main:app --port 8765 --reload

# Frontend (andere terminal)
cd frontend
npm install
API_URL=http://127.0.0.1:8765 npm run dev
```

## Structuur

```
backend/app/
  main.py          FastAPI-app
  models.py        tabellen: users, sessions, members, columns, counter
  auth.py          wachtwoorden (Argon2), sessiecookies, rolcontrole, rate limiting
  routers/         API-endpoints per onderdeel
  cli.py           init-db, create-admin
frontend/src/
  views/           pagina's
  components/      teller-bord, columnkaart, logo
  site.js          contactgegevens voor het privacybeleid
```

Tabellen worden aangemaakt met `create_all`. Verander je later een bestaande tabel, voeg dan Alembic toe voor migraties.
