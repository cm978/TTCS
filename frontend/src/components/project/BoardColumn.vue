<template>
  <article class="board-column" :class="`board-column--${column.status.toLowerCase().replace('_', '-')}`">
    <header>
      <span class="status-dot" aria-hidden="true" />
      <div>
        <h2>{{ column.name }}</h2>
        <p>{{ statusLabel(column.status) }} · 0</p>
      </div>
    </header>
    <div class="empty-state">
      <h3>{{ emptyTitle(column.status) }}</h3>
      <p>任务功能将在后续阶段接入。当前看板列已准备就绪。</p>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { BoardColumn, BoardColumnStatus } from "../../types/project";

defineProps<{ column: BoardColumn }>();

function statusLabel(status: BoardColumnStatus) {
  const labels: Record<BoardColumnStatus, string> = {
    TODO: "待办",
    IN_PROGRESS: "进行中",
    IN_REVIEW: "待验收",
    REJECTED: "打回修改",
    DONE: "已完成"
  };
  return labels[status];
}

function emptyTitle(status: BoardColumnStatus) {
  const titles: Record<BoardColumnStatus, string> = {
    TODO: "暂无待办任务",
    IN_PROGRESS: "暂无进行中的任务",
    IN_REVIEW: "暂无待验收任务",
    REJECTED: "暂无打回修改任务",
    DONE: "暂无已完成任务"
  };
  return titles[status];
}
</script>

<style scoped>
.board-column {
  min-width: 220px;
  min-height: 320px;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-top: 4px solid var(--column-accent, var(--color-border));
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.board-column--todo {
  --column-accent: var(--color-text-muted);
}

.board-column--in-progress {
  --column-accent: var(--color-primary);
}

.board-column--in-review {
  --column-accent: var(--color-review);
}

.board-column--rejected {
  --column-accent: var(--color-danger);
}

.board-column--done {
  --column-accent: var(--color-success);
}

header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.status-dot {
  width: 10px;
  height: 10px;
  margin-top: 8px;
  border-radius: 999px;
  background: var(--column-accent);
}

h2,
h3,
p {
  margin: 0;
}

h2 {
  color: var(--color-text);
  font-size: 16px;
}

header p,
.empty-state p {
  color: var(--color-text-muted);
  font-size: 14px;
  line-height: 1.5;
}

.empty-state {
  display: grid;
  align-content: center;
  gap: 8px;
  min-height: 180px;
  padding: 16px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
}

.empty-state h3 {
  color: var(--color-text);
  font-size: 15px;
}
</style>
