<script setup>
import { SITE } from '../site'
</script>

<template>
  <div class="narrow page">
    <span class="eyebrow">Laatst bijgewerkt: {{ SITE.privacyUpdated }}</span>
    <h1>Privacybeleid</h1>
    <p class="lead">
      Kort gezegd: we slaan zo min mogelijk op, we volgen je niet, we verkopen niks en we delen niks. Hieronder staat precies
      welke gegevens deze website bewaart, waarom, en hoe lang.
    </p>

    <div class="prose">
      <h2>Wie zijn wij?</h2>
      <p>
        Deze website is van de Trauma Tram Tellers (TTT), een vriendengroep uit Amsterdam. Het bestuur van de TTT is
        verantwoordelijk voor de verwerking van persoonsgegevens op deze site. Vragen? Mail naar
        <a :href="`mailto:${SITE.contactEmail}`">{{ SITE.contactEmail }}</a>.
      </p>

      <h2>Welke gegevens slaan we op?</h2>
    </div>

    <div class="data-table card table-scroll">
      <table>
        <thead>
          <tr><th>Wat</th><th>Welke gegevens</th><th>Waarom</th><th>Hoe lang</th></tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Je account</strong></td>
            <td>Naam, e-mailadres, wachtwoord (alleen als onomkeerbare Argon2-hash), rol, status, datum van aanmelden, goedkeuren en laatste login.</td>
            <td>Om je te laten inloggen en te bepalen wat je mag zien en doen.</td>
            <td>Tot je je account verwijdert of een admin dat doet.</td>
          </tr>
          <tr>
            <td><strong>Sessiecookie</strong></td>
            <td>Eén cookie (<code>ttt_session</code>) met een willekeurige code. Op de server staat alleen een hash daarvan, met een vervaldatum.</td>
            <td>Om je ingelogd te houden. Dit is een strikt noodzakelijke cookie, daarom vragen we er geen toestemming voor.</td>
            <td>Maximaal 30 dagen, of tot je uitlogt.</td>
          </tr>
          <tr>
            <td><strong>Ledenadministratie</strong></td>
            <td>Naam, bijnaam, functie, dienstdag, lid-sinds-datum, actief/oud-lid, eventueel een koppeling met een account en interne notities.</td>
            <td>Om bij te houden wie er lid is en wie welke dagdienst draait.</td>
            <td>Zolang je lid bent. Oud-leden worden op verzoek verwijderd.</td>
          </tr>
          <tr>
            <td><strong>Columns</strong></td>
            <td>Titel, tekst, naam van de schrijver, datum. Intern ook welk account de column heeft geplaatst of het laatst bewerkt.</td>
            <td>Om de columns te publiceren.</td>
            <td>Tot de column wordt verwijderd.</td>
          </tr>
          <tr>
            <td><strong>IP-adres</strong></td>
            <td>Je IP-adres, alleen in het werkgeheugen van de server.</td>
            <td>Om te voorkomen dat iemand eindeloos wachtwoorden probeert bij inloggen en aanmelden.</td>
            <td>Maximaal 1 uur, en het wordt nooit naar schijf of database geschreven.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="prose">
      <h2>Wie kan wat zien?</h2>
      <ul>
        <li><strong>Iedereen:</strong> de homepage, de teller, de columns (inclusief de voornaam van de schrijver), deze pagina en de over-ons-pagina.</li>
        <li><strong>Goedgekeurde leden:</strong> daarnaast de ledenadministratie (zonder notities).</li>
        <li><strong>Admins:</strong> daarnaast alle accounts met e-mailadres, de notities in de ledenadministratie en welk account bij welk lid hoort.</li>
      </ul>
      <p>Zolang je account nog niet is goedgekeurd, kun je niet inloggen en zie je dus niks extra's.</p>

      <h2>Wat we níet doen</h2>
      <ul>
        <li>Geen analytics, trackers, advertenties of social-media-knoppen.</li>
        <li>Geen externe lettertypes of scripts: alles wordt vanaf onze eigen server geladen, dus je browser praat met niemand anders.</li>
        <li>Geen toegangslogboeken met IP-adressen in onze applicatie.</li>
        <li>We verkopen of delen je gegevens met niemand.</li>
      </ul>

      <h2>Waar staan de gegevens?</h2>
      <p>
        Alles staat in één database op de server van {{ SITE.hostingProvider }}. Die partij verwerkt de gegevens alleen in onze
        opdracht. De verbinding met de site is altijd versleuteld (HTTPS).
      </p>

      <h2>Grondslag</h2>
      <p>
        We verwerken accountgegevens en de ledenadministratie omdat dat nodig is om de vereniging (en deze site) te laten
        draaien: ons gerechtvaardigd belang, en jouw keuze om je aan te melden. Je kunt dat op elk moment beëindigen door je
        account te verwijderen.
      </p>

      <h2>Jouw rechten</h2>
      <p>Op grond van de AVG heb je het recht om:</p>
      <ul>
        <li><strong>je gegevens in te zien</strong>: via <em>Mijn account → Gegevens downloaden</em>, of vraag het bestuur om je gegevens uit de ledenadministratie;</li>
        <li><strong>gegevens te laten corrigeren</strong>: je naam en wachtwoord pas je zelf aan, voor de rest mail je het bestuur;</li>
        <li><strong>gegevens te laten verwijderen</strong>: via <em>Mijn account → Account verwijderen</em>, of op verzoek voor ledenadministratie en columns;</li>
        <li><strong>bezwaar te maken</strong> tegen een verwerking, en een klacht in te dienen bij de <a href="https://autoriteitpersoonsgegevens.nl" rel="noopener">Autoriteit Persoonsgegevens</a>.</li>
      </ul>
      <p>We reageren binnen een maand op verzoeken.</p>

      <h2>Beveiliging</h2>
      <p>
        Wachtwoorden worden alleen als Argon2-hash opgeslagen, de sessiecookie is niet uit te lezen door JavaScript en wordt
        alleen via HTTPS verstuurd, en elke actie wordt op de server gecontroleerd op je rol (lid, editor of admin).
      </p>

      <h2>Wijzigingen</h2>
      <p>Als we dit beleid aanpassen, zie je dat aan de datum bovenaan deze pagina.</p>
    </div>
  </div>
</template>

<style scoped>
.data-table { padding: 8px 16px; margin-bottom: 24px; width: min(960px, 100vw - 32px); margin-left: 50%; transform: translateX(-50%); }
.data-table td { font-size: 0.92rem; }
.data-table td:first-child { white-space: nowrap; }
code { font-size: 0.9em; background: var(--line); padding: 1px 5px; border-radius: 4px; }
</style>
