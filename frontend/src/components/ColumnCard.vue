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
      <span v-if="column.has_incident" class="sticker">Sticker geplakt</span>
      <h3>{{ column.title }}</h3>
      <p>{{ column.excerpt }}</p>
      <div class="foot">
        <span class="more">Lees verder →</span>
        <span v-if="column.like_count || column.comment_count" class="stats small">
          <span :title="`${column.like_count} keer leuk gevonden`">♥ {{ column.like_count }}</span>
          <span :title="`${column.comment_count} reacties`">💬 {{ column.comment_count }}</span>
        </span>
      </div>
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
.sticker { align-self: flex-start; margin-bottom: 8px; padding: 2px 10px; border-radius: 999px; background: var(--alarm); color: #fff; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
p { font-family: var(--serif); color: var(--ink-soft); font-size: 1rem; line-height: 1.6; flex: 1; }
.foot { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.stats { display: inline-flex; gap: 10px; color: var(--muted); font-weight: 600; }
.more { font-weight: 700; font-size: 0.85rem; }
</style>
