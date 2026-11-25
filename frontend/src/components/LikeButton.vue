<script setup>
import { computed, ref } from 'vue'
import { api } from '../api'

// `path` is bijv. "/columns/3/like" of "/comments/7/like".
const props = defineProps({
  path: { type: String, required: true },
  likes: { type: Object, required: true }, // { count, liked, names }
  small: Boolean,
})
const emit = defineEmits(['update'])
const busy = ref(false)

const who = computed(() => {
  const n = props.likes.names
  if (!n.length) return 'Nog niemand vindt dit leuk'
  if (n.length <= 3) return `${n.join(', ')} vind${n.length === 1 ? 't' : 'en'} dit leuk`
  return `${n.slice(0, 3).join(', ')} en ${n.length - 3} anderen vinden dit leuk`
})

async function toggle() {
  if (busy.value) return
  busy.value = true
  try {
    emit('update', await api(props.path, { method: props.likes.liked ? 'DELETE' : 'PUT' }))
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <button
    type="button"
    class="like"
    :class="{ on: likes.liked, small }"
    :aria-pressed="likes.liked"
    :title="who"
    :aria-label="`${likes.liked ? 'Niet meer leuk' : 'Leuk'} · ${who}`"
    @click="toggle"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 5 6.4 5c2 0 3.4 1.1 4.1 2.3h3c.7-1.2 2.1-2.3 4.1-2.3C21 5 23.1 8.4 21.6 11.8 19.5 16.4 12 21 12 21z" />
    </svg>
    <span>{{ likes.count }}</span>
  </button>
</template>

<style scoped>
.like {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  color: var(--ink);
  font: 600 0.9rem var(--sans);
  cursor: pointer;
  transition: border-color 0.12s ease, transform 0.12s ease;
}
.like:hover { border-color: var(--alarm); }
.like:active { transform: scale(0.95); }
.like svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; }
.like.on { border-color: var(--alarm); color: var(--alarm); }
.like.on svg { fill: var(--alarm); stroke: var(--alarm); }
.like.small { padding: 2px 8px; font-size: 0.8rem; border-width: 1px; }
.like.small svg { width: 14px; height: 14px; }
</style>
