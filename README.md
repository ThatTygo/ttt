# Trauma Tram Tellers

Website van de TTT: intro, over ons, privacybeleid, columns, dienstrooster en een afgeschermde ledenadministratie.

- **Frontend:** Vue 3 + Vite (`frontend/`), gebouwd tot statische bestanden
- **Backend:** PHP 8.1+ zonder framework (`api/`)
- **Database:** MySQL / MariaDB
- **Hosting:** gewone Strato-webhosting (Apache + PHP + MySQL), geen eigen server nodig

## Rollen

| Rol | Mag |
| --- | --- |
| *bezoeker* | Home, columns, over ons, privacy lezen |
| `user` | inloggen, eigen account beheren |
| `editor` | + columns schrijven/bewerken/verwijderen, teller bijwerken, dienstrooster bekijken |
| `admin` | + accounts goedkeuren, rollen wijzigen, ledenadministratie bekijken en beheren |

Nieuwe accounts krijgen de rol `user` met status *pending* en kunnen pas inloggen nadat een admin ze heeft goedgekeurd (menu **Accounts**).

## Live zetten op Strato

Je hebt een Strato-pakket met webruimte, PHP en MySQL nodig. Alleen een domein ("Domain"-pakket) is niet genoeg.

### Eenmalig in het Strato-panel

1. **PHP-versie:** zet de PHP-versie op 8.2 of hoger.
2. **SSL:** activeer het gratis SSL-certificaat voor je domein.
3. **Database:** maak onder *Databases* een MySQL-database aan. Noteer de host, de databasenaam, de gebruiker en het wachtwoord.
4. **Webroot:** kijk bij *Domeinen* naar welke map je domein wijst (bijv. `/ttt`). Daar komt de site in.

### Bouwen en uploaden

1. Pas het contactadres in `frontend/src/site.js` aan (dat komt in het privacybeleid) en bouw de site op je eigen computer (Node.js nodig):
   ```bash
   ./build.sh
   ```
   Dit maakt de map `deploy/` aan.
2. Maak `config.php` aan: kopieer `api/config.sample.php` naar `deploy/api/config.php` en vul in:
   - de databasegegevens uit stap 3;
   - `secret` en `install_key`: twee lange willekeurige teksten, bijv. via `php -r 'echo bin2hex(random_bytes(32));'` of een wachtwoordgenerator.
3. Upload de **inhoud** van `deploy/` via SFTP (bijv. met FileZilla, host `ssh.strato.de`) naar de webroot van je domein. Let op dat de verborgen `.htaccess`-bestanden mee gaan.
4. Ga naar `https://jouwdomein.nl/api/install.php` en vul de installatiecode (`install_key`), je naam, e-mailadres en wachtwoord in. Hiermee worden de tabellen aangemaakt, de columns en leden uit de groepsapp ingeladen en word jij admin.
5. Verwijder `api/install.php` van de server. Zodra er een admin is, weigert het bestand overigens toch elke nieuwe installatie.

### Updaten

```bash
./build.sh
```

Upload daarna de inhoud van `deploy/` opnieuw. `config.php` zit niet in `deploy/`, dus die op de server blijft staan.

### Back-up

Maak via *Databases* in het Strato-panel (phpMyAdmin → Exporteren) af en toe een back-up.

## Lokaal ontwikkelen

```bash
# Database
docker run -d --name ttt-mysql -e MYSQL_DATABASE=ttt -e MYSQL_USER=ttt -e MYSQL_PASSWORD=ttt -e MYSQL_ROOT_PASSWORD=root -p 127.0.0.1:53306:3306 mysql:8.0

# Config: kopieer api/config.sample.php naar api/config.php
#   host 127.0.0.1, port 53306, name/user/password ttt, cookie_secure false

# Backend (PHP's ingebouwde server)
php -S 127.0.0.1:8765 api/index.php
# Installeren: open http://127.0.0.1:8765/api/install.php

# Frontend (andere terminal)
cd frontend
npm install
API_URL=http://127.0.0.1:8765 npm run dev
```

## Structuur

```
api/
  index.php           router: alle /api/*-verzoeken
  install.php         eenmalige installatie
  config.sample.php   voorbeeld voor config.php (die niet in git staat)
  .htaccess           stuurt alles naar index.php, schermt config en src/ af
  src/
    bootstrap.php     database, validatie, JSON-responses
    auth.php          wachtwoorden, sessiecookies, rolcontrole, rate limiting
    handlers/         endpoints per onderdeel
    schema.sql        tabellen
    seed.json         startinhoud (leden + columns uit de groepsapp)
frontend/
  public/.htaccess    HTTPS, Vue-router-fallback, security headers
  src/views/          pagina's
  src/site.js         contactgegevens voor het privacybeleid
build.sh              bouwt deploy/ om te uploaden
```

Wil je later een tabel aanpassen, voer de wijziging dan uit via phpMyAdmin en werk `api/src/schema.sql` bij.

De eerdere versie met een Python-backend en Docker (voor een eigen server) staat in de git-geschiedenis, commit `9916457`.
