<template>
  <section class="blocker-timeline">
    <h3>阻塞历史</h3>
    <div v-if="blockers.length === 0" class="empty">暂无阻塞记录</div>
    <article v-for="log in blockers" :key="log.id" class="blocker-item" :class="{ resolved: Boolean(log.resolved_at) }">
      <strong>{{ log.resolved_at ? "已解除" : "阻塞中" }}</strong>
      <p>{{ log.blocked_reason }}</p>
      <p v-if="log.resolved_at">处理说明：{{ log.resolution_note }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { WorkLog } from "../../types/task";

const props = defineProps<{ logs: WorkLog[] }>();
const blockers = computed(() => props.logs.filter((log) => log.is_blocked));
</script>

<style scoped>
.blocker-timeline {
  display: grid;
  gap: 10px;
}

h3,
p {
  margin: 0;
}

.empty {
  color: var(--color-text-muted);
}

.blocker-item {
  display: grid;
  gap: 6px;
  padding: 12px;
  border: 1px solid color-mix(in srgb, var(--color-warning) 35%, var(--color-border));
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-warning) 8%, var(--color-surface));
}

.blocker-item strong {
  color: var(--color-warning);
}

.blocker-item.resolved {
  border-color: var(--color-border);
  background: var(--color-surface-raised);
}

.blocker-item.resolved strong {
  color: var(--color-success);
}
</style>
