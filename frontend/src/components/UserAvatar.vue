<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: { type: Object, required: true }, // { id, name, avatar_url }
  size: { type: Number, default: 40 },
})

const initials = computed(() =>
  props.user.name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join(''),
)
// Vaste kleur per persoon, zodat initialen herkenbaar blijven.
const hue = computed(() => ((props.user.id || 0) * 67) % 360)
</script>

<template>
  <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.name" class="avatar" :style="{ width: `${size}px`, height: `${size}px` }" />
  <span
    v-else
    class="avatar initials"
    role="img"
    :aria-label="user.name"
    :style="{ width: `${size}px`, height: `${size}px`, fontSize: `${size * 0.4}px`, '--hue': hue }"
  >{{ initials }}</span>
</template>

<style scoped>
.avatar { border-radius: 50%; object-fit: cover; flex: none; display: inline-block; background: var(--line); }
.initials {
  display: inline-grid;
  place-items: center;
  font-family: var(--display);
  letter-spacing: 0.04em;
  padding-top: 0.08em;
  color: #fff;
  background: hsl(var(--hue) 45% 38%);
}
</style>
