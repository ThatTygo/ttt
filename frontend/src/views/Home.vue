<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { auth } from '../auth'
import ColumnCard from '../components/ColumnCard.vue'
import CounterBoard from '../components/CounterBoard.vue'

const counter = ref(null)
const latest = ref([])
const total = ref(0)

onMounted(async () => {
  const [c, cols] = await Promise.all([api('/counter'), api('/columns?limit=3')])
  counter.value = c
  latest.value = cols.items
  total.value = cols.total
})
</script>

<template>
  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <span class="eyebrow">Opgericht in Amsterdam · sinds oktober 2026</span>
        <h1>Trauma<br />Tram <span class="hl">Tellers</span></h1>
        <p class="lead">
          Elke dag houdt één van ons de Nederlandse trambanen in de gaten. Is er een incident? Dan wordt het gelogd,
          komt er een sticker op de muur en springt de teller. Is er niks? Dan schrijven we daar een column over.
          Spoiler: er is meestal niks.
        </p>
        <div class="row">
          <RouterLink to="/columns" class="btn signal">Lees de columns</RouterLink>
          <RouterLink v-if="!auth.user" to="/aanmelden" class="btn ghost">Word lid</RouterLink>
          <RouterLink v-else-if="auth.can('editor')" to="/columns/nieuw" class="btn ghost">Schrijf een column</RouterLink>
        </div>
      </div>
      <CounterBoard :counter="counter" @updated="counter = $event" />
    </div>
    <div class="rails" aria-hidden="true" />
  </section>

  <section class="wrap how">
    <div class="step">
      <span class="num">01</span>
      <h3>Dagdienst</h3>
      <p>Iedere dag van de week heeft een vaste teller. Die speurt het nieuws af naar tramincidenten in Amsterdam en omstreken.</p>
    </div>
    <div class="step">
      <span class="num">02</span>
      <h3>Legitiem loggen</h3>
      <p>Eerst de artikellink delen, dán pas plakken. Zo voorkomen we dubbele stickers. AD.nl alleen als niemand anders het heeft.</p>
    </div>
    <div class="step">
      <span class="num">03</span>
      <h3>De column</h3>
      <p>Aan het einde van de dienst volgt het verslag. Meestal met de mededeling dat de teller op nul (zegge 0) blijft steken.</p>
    </div>
  </section>

  <section class="wrap latest">
    <div class="row spread head">
      <div>
        <span class="eyebrow">Uit de dagdienst</span>
        <h2>Laatste columns</h2>
      </div>
      <RouterLink to="/columns" class="all">Alle {{ total }} columns →</RouterLink>
    </div>
    <div class="cards">
      <ColumnCard v-for="c in latest" :key="c.id" :column="c" />
    </div>
    <p v-if="!latest.length" class="card muted">Nog geen columns. De eerste dagdienst moet nog beginnen.</p>
  </section>

  <section class="wrap quote-wrap">
    <blockquote>
      <p>Houd moed, TTT'ers. De stilte is tijdelijk, de traditie is eeuwig.</p>
      <cite>— Vaste afsluiter van de dagdienst</cite>
    </blockquote>
  </section>
</template>

<style scoped>
.hero { position: relative; padding: 56px 0 72px; overflow: hidden; }
.hero-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 48px; align-items: center; }
h1 { font-size: clamp(3.6rem, 9vw, 6.6rem); line-height: 0.9; margin-bottom: 20px; }
.hl { background: linear-gradient(transparent 58%, var(--signal) 58%, var(--signal) 90%, transparent 90%); padding: 0 4px; }
.lead { margin-bottom: 28px; }
.rails {
  position: absolute; left: 0; right: 0; bottom: 18px; height: 14px;
  background:
    linear-gradient(var(--ink), var(--ink)) 0 0 / 100% 2px no-repeat,
    linear-gradient(var(--ink), var(--ink)) 0 100% / 100% 2px no-repeat,
    repeating-linear-gradient(90deg, var(--line) 0 6px, transparent 6px 28px);
  opacity: 0.5;
}
@media (max-width: 860px) {
  .hero-grid { grid-template-columns: 1fr; gap: 36px; }
}

.how { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding-block: 24px 56px; }
.step { border-top: 3px solid var(--ink); padding-top: 16px; }
.num { font-family: var(--display); font-size: 1.1rem; color: var(--muted); letter-spacing: 0.1em; }
.step p { color: var(--ink-soft); }
@media (max-width: 760px) { .how { grid-template-columns: 1fr; } }

.latest { padding-bottom: 56px; }
.head { align-items: end; margin-bottom: 20px; }
.all { font-weight: 700; text-decoration: none; }
.cards { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }

.quote-wrap { padding-bottom: 72px; }
blockquote { margin: 0; padding: 40px clamp(20px, 5vw, 56px); background: var(--signal); color: var(--signal-ink); border-radius: 20px; }
blockquote p { font-family: var(--display); font-size: clamp(2rem, 5vw, 3.4rem); line-height: 1; margin-bottom: 12px; }
cite { font-style: normal; font-weight: 600; font-size: 0.9rem; }
</style>
