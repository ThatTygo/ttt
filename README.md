# Trauma Tram Tellers

Website van de TTT: intro, over ons, privacybeleid, columns, Pimpy (notulen, taken en agenda) en een afgeschermde ledenadministratie.

- **Frontend:** Vue 3 + Vite (`frontend/`)
- **Backend:** Python, FastAPI + SQLAlchemy (`backend/`)
- **Database:** PostgreSQL
- **Productie:** Docker Compose met Caddy (automatisch HTTPS via Let's Encrypt)

## Rollen

| Rol | Mag |
| --- | --- |
| *bezoeker* | Home (met teller), over ons, privacy lezen |
| `user` | + columns lezen, eigen account beheren |
| `editor` | + columns schrijven/bewerken/verwijderen (met "incident"-vinkje dat de teller bijwerkt), teller bijwerken, dienstrooster bekijken, Pimpy van de eigen groepen |
| `admin` | + accounts goedkeuren, rollen wijzigen, ledenadministratie bekijken en beheren, Pimpy-groepen beheren en alles in Pimpy zien |

Nieuwe accounts krijgen de rol `user` met status *pending* en kunnen pas inloggen nadat een admin ze heeft goedgekeurd (menu **Accounts**).

## Meldingen

Iedere ingelogde gebruiker kan met de knop **Melden** (rechtsonder op elke pagina) een bug, idee of vraag melden; de huidige pagina wordt automatisch meegestuurd. Onder **Mijn meldingen** volg je de status en kun je reageren. Admins zien onder **Meldingen** (met een teller voor nieuwe meldingen) alles, stellen status, prioriteit en behandelaar in, en kunnen interne notities maken die de melder niet ziet. Reageert de melder op een opgeloste melding, dan gaat hij weer open.

Als mail aanstaat (zie Pimpy) krijgen admins een mail bij een nieuwe melding, en de melder bij een antwoord of statuswijziging.

## Pimpy

Naar het voorbeeld van Pimpy in [viaduct](https://gitlab.com/studieverenigingvia/viaduct). Admins maken onder **Pimpy → Groepen** groepen aan (bijv. Bestuur) en kiezen de leden (editors en admins). Per groep voer je notulen in; regels in hoofdletters worden automatisch verwerkt:

| Regel | Effect |
| --- | --- |
| `ACTIE Robin, Gijs: stickers bestellen` | Eén taak voor Robin en Gijs samen |
| `ACTIES Robin, Gijs: notulen lezen` | Een aparte taak voor elk van hen |
| `ACTIE: domein verlengen` | Taak voor de hele groep |
| `DONE 1A, 2B` | Taken met deze codes worden afgerond |
| `REMOVE 3C` | Taken met deze codes vervallen |
| `MEETING 26-11-2026 13:30(2) Vergadering` | Vergadering op de agenda (duur in uren, standaard 1) |

Nederlandse varianten werken ook: `TAAK`/`TAKEN`, `KLAAR`, `VERVALT`, `VERGADERING`. Namen worden vergeleken met de leden van de groep, dus een voornaam of kleine tikfout is genoeg. Tijdens het typen laat de site zien wat er gaat gebeuren en welke regels fout zijn.

Wie een taak krijgt, kan een mail ontvangen. Vul daarvoor de `SMTP_*`-regels in `.env` in (zie `.env.example`); zonder SMTP werkt alles behalve de mail. Iedereen kan de mails uitzetten onder **Mijn account**.

**Mailen via Postfix op dezelfde server.** De API-container bereikt de server via `host.docker.internal`. Zet in `.env`:

```
SMTP_HOST=host.docker.internal
SMTP_PORT=25
SMTP_SECURITY=none
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=Trauma Tram Tellers <ict@traumatramtellers.nl>
```

Postfix moet dan luisteren op meer dan alleen `localhost` en mail van de Docker-netwerken (`172.16.0.0/12`) accepteren, en de firewall moet poort 25 vanuit die netwerken toelaten:

```bash
sudo postconf -e 'inet_interfaces = all'
sudo postconf -e "mynetworks = $(postconf -h mynetworks) 172.16.0.0/12"
sudo systemctl restart postfix
sudo ufw allow from 172.16.0.0/12 to any port 25 proto tcp
```

Poort 25 blijft voor de buitenwereld dicht zolang de firewall alleen 22, 80 en 443 open heeft.

## Wiki

Op `wiki.<domein>` draait [DokuWiki](https://www.dokuwiki.org) (map `wiki/`), alleen voor editors en admins. Er zijn geen aparte wiki-accounts: Caddy vraagt bij elk verzoek aan de API wie er is ingelogd (`/api/auth/wiki`, via `forward_auth`) en geeft naam en rol door aan DokuWiki (plugin `wiki/authttt`). Niet ingelogd → door naar het inlogscherm van de site en daarna terug naar de wiki. Admins zijn superuser in de wiki.

Daarvoor geldt de sessiecookie ook op `wiki.<domein>` (`COOKIE_DOMAIN` in `docker-compose.yml`). De wiki-container is alleen via Caddy bereikbaar en de wikidata staat in het volume `wiki-data`.

Nodig in DNS: een A-record (en AAAA) voor `wiki` naar de server, of een CNAME `wiki` → `@`.

## Live zetten

1. **Server:** installeer Docker (`curl -fsSL https://get.docker.com | sh`) en zet deze repo erop.
2. **DNS:** maak een A-record voor `@` en `www` naar het IP-adres van de server (en AAAA bij IPv6).
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

Back-up van de database en de wiki:
```bash
docker compose exec db pg_dump -U ttt ttt > backup.sql
docker compose exec wiki tar czf - -C /storage data conf > wiki-backup.tar.gz
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
  models.py        tabellen: users, sessions, members, columns, counter, groups, minutes, tasks, meetings
  auth.py          wachtwoorden (Argon2), sessiecookies, rolcontrole, rate limiting
  routers/         API-endpoints per onderdeel
  pimpy.py         notulen lezen: ACTIE/DONE/REMOVE/MEETING-regels
  mail.py          e-mail via SMTP
  cli.py           init-db, create-admin
frontend/src/
  views/           pagina's (views/pimpy/ voor Pimpy)
  components/      teller-bord, columnkaart, logo
  site.js          contactgegevens voor het privacybeleid
```

Tabellen worden aangemaakt met `create_all`. Nieuwe kolommen in bestaande tabellen staan als `ALTER TABLE … IF NOT EXISTS` in `MIGRATIONS` in `cli.py` en worden bij elke start uitgevoerd.
