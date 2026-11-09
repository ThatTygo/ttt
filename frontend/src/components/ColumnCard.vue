<script setup>
import { formatDate } from '../format'

defineProps({ column: { type: Object, required: true } })
</script>

<template>
  <article class="column-card">
    <RouterLink :to="`/columns/${column.id}`" class="cover">
      <div class="meta">
        <span class="author">{{ column.author_name }}</span>
        <time :datetime="column.published_at">{{ formatDate(column.published_at) }}</time>
      </div>
      <h3>{{ column.title }}</h3>
      <p>{{ column.excerpt }}</p>
      <span class="more">Lees verder →</span>
    </RouterLink>
  </article>
</template>

<style scoped>
.column-card { height: 100%; }
.cover {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 22px 22px 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  text-decoration: none;
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.cover:hover { transform: translateY(-3px); border-color: var(--signal); }
.meta { display: flex; justify-content: space-between; gap: 8px; font-size: 0.8rem; color: var(--muted); margin-bottom: 12px; }
.author { font-weight: 700; color: var(--ink); background: var(--signal); color: var(--signal-ink); padding: 1px 8px; border-radius: 6px; }
h3 { font-size: 1.7rem; }
p { font-family: var(--serif); color: var(--ink-soft); font-size: 1rem; line-height: 1.6; flex: 1; }
.more { font-weight: 700; font-size: 0.85rem; }
</style>
