<script setup>
const timeline = [
  { date: 'Begin oktober 2026', text: 'De eerste stickers gaan op de muur in de kelder. Een ontspoorde tram op de Van Baerlestraat zet de toon.' },
  { date: '10 oktober 2026', text: 'Het dienstrooster wordt vastgesteld: elke dag van de week een vaste teller. Diezelfde nacht verschijnt de allereerste column.' },
  { date: '12 oktober 2026', text: 'De richtlijnen voor legitiem loggen worden afgekondigd. Er wordt een biertje uitgeloofd voor de eerste die een sticker plakt.' },
  { date: '3 november 2026', text: 'Eerste officiële vergadering in L1.07. Het bestuur wordt geboren, de notulen worden gemaakt en een tram wordt gedoopt tot “rail god”.' },
  { date: '5 november 2026', text: 'Eerste borrel als bestuur (business casual, colbert aan) en een eigen community voor de columns.' },
  { date: '9 november 2026', text: 'Eigen domein, eigen website. Het getingel in de verte komt dichterbij.' },
]
</script>

<template>
  <div class="page">
    <div class="narrow">
      <span class="eyebrow">Over ons</span>
      <h1>Wie zijn de Trauma Tram Tellers?</h1>
      <p class="lead">
        Een Amsterdamse vriendengroep met een bijzondere hobby: het bijhouden van tramincidenten in Nederland, en dan vooral
        het uitblijven ervan.
      </p>

      <div class="prose">
        <p>
          Het begon met een muur in de kelder en een rol stickers. Voor ieder legitiem gelogd tramincident komt er één bij.
          Al snel bleek dat de Amsterdamse trams verrassend goed hun best doen om op de rails te blijven, en zo ontstond de
          belangrijkste traditie van de TTT: de dagelijkse column.
        </p>
        <p>
          Elke dag van de week heeft een vaste teller. Die houdt de dagdienst: het nieuws afspeuren, de omstandigheden
          beoordelen (gladheid, ADE, Halloween, een landelijke staking) en aan het einde van de dag verslag uitbrengen. Dat
          verslag eindigt opvallend vaak met de mededeling dat de teller op nul (zegge 0) blijft steken.
        </p>
        <p>
          Inmiddels heeft de TTT een heus bestuur, een voorzitter, notulen, een eigen community en nu dus ook een eigen
          website. Wat begon als een grap, is een traditie geworden. En de traditie is eeuwig.
        </p>
      </div>
    </div>

    <section class="wrap rules">
      <div class="card rules-card">
        <span class="eyebrow">Officieel vastgesteld op 12 oktober 2026</span>
        <h2>Richtlijnen voor legitiem loggen</h2>
        <ol>
          <li><strong>Eerst de link, dan de sticker.</strong> Deel altijd eerst een link naar een nieuwsartikel in de groep voordat je een sticker plakt. Zo voorkomen we dubbel plakken.</li>
          <li><strong>Geen AD.nl.</strong> Tenzij er geen enkele andere digitale pers over het betreffende incident heeft geschreven.</li>
          <li><strong>Het moet een tram zijn.</strong> Barneveld heeft geen tram. Hoe glad het daar ook is.</li>
          <li><strong>Eén incident, één sticker.</strong> En de eerste die plakt, krijgt een biertje van de voorzitter.</li>
        </ol>
      </div>
    </section>

    <section class="narrow">
      <h2>Tijdlijn</h2>
      <ol class="timeline">
        <li v-for="t in timeline" :key="t.date">
          <span class="stop" aria-hidden="true" />
          <div>
            <strong>{{ t.date }}</strong>
            <p>{{ t.text }}</p>
          </div>
        </li>
      </ol>

      <div class="disclaimer card">
        <h3>Even serieus</h3>
        <p>
          De TTT is een humoristische vriendengroep. We wensen niemand letsel toe en we hebben niks tegen trambestuurders,
          fietsers, toeristen of demonstranten. We halen onze informatie uitsluitend uit openbaar nieuws. Kijk dus gewoon
          goed uit bij het oversteken: de Siemens Combino is 29,2 meter lang en remt beter dan je denkt.
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.prose { margin-top: 28px; }
.rules { padding-block: 40px; }
.rules-card { background: var(--ink); color: var(--paper); border: 0; padding: clamp(24px, 5vw, 48px); }
.rules-card .eyebrow { color: var(--signal); }
.rules-card ol { counter-reset: r; list-style: none; padding: 0; margin: 20px 0 0; display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }
.rules-card li { counter-increment: r; padding-top: 12px; border-top: 2px solid var(--signal); }
.rules-card li::before { content: counter(r, decimal-leading-zero); display: block; font-family: var(--display); font-size: 2rem; color: var(--signal); line-height: 1; margin-bottom: 6px; }
.rules-card strong { display: block; margin-bottom: 4px; }

.timeline { list-style: none; padding: 0; margin: 16px 0 40px; position: relative; }
.timeline::before { content: ''; position: absolute; left: 8px; top: 8px; bottom: 8px; width: 3px; background: repeating-linear-gradient(var(--ink) 0 10px, transparent 10px 16px); opacity: 0.35; }
.timeline li { display: flex; gap: 20px; padding-bottom: 20px; position: relative; }
.stop { flex: none; width: 19px; height: 19px; border-radius: 50%; background: var(--signal); border: 3px solid var(--ink); margin-top: 3px; }
.timeline p { margin: 2px 0 0; color: var(--ink-soft); }
.disclaimer { border-left: 4px solid var(--signal); }
.disclaimer p { margin: 0; color: var(--ink-soft); }
</style>
