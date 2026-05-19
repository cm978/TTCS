<template>
  <section class="subtask-checklist">
    <header>
      <h3>子任务</h3>
      <span>{{ completed }}/{{ subtasks.length }} 已完成</span>
    </header>
    <div v-if="subtasks.length === 0" class="empty">暂无子任务</div>
    <label v-for="subtask in subtasks" :key="subtask.id" class="subtask-row" :class="{ 'subtask-row--done': subtask.is_completed }">
      <input
        class="subtask-checkbox"
        type="checkbox"
        :checked="subtask.is_completed"
        :disabled="updatingId === subtask.id"
        @change="handleToggle(subtask, $event)"
      />
      <span class="subtask-title">{{ subtask.title }}</span>
      <span class="subtask-status">{{ subtask.is_completed ? "已完成" : "未完成" }}</span>
    </label>
    <div class="add-row">
      <a-input v-model:value="newTitle" placeholder="新增子任务" @press-enter="handleAdd" />
      <a-button :disabled="newTitle.trim().length < 2" @click="handleAdd">添加</a-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import type { Subtask } from "../../types/task";

const props = defineProps<{ subtasks: Subtask[]; updatingId?: number | null }>();
const emit = defineEmits<{ add: [title: string]; toggle: [subtask: Subtask, isCompleted: boolean] }>();
const newTitle = ref("");
const completed = computed(() => props.subtasks.filter((subtask) => subtask.is_completed).length);

function handleAdd() {
  const title = newTitle.value.trim();
  if (title.length < 2) {
    return;
  }
  emit("add", title);
  newTitle.value = "";
}

function handleToggle(subtask: Subtask, event: Event) {
  emit("toggle", subtask, Boolean((event.target as HTMLInputElement | null)?.checked));
}
</script>

<style scoped>
.subtask-checklist {
  display: grid;
  gap: 10px;
}

header,
.add-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

h3 {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
}

header span,
.empty {
  color: var(--color-text-muted);
  font-size: 14px;
}

.subtask-row {
  min-height: 44px;
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
}

.subtask-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

.subtask-title {
  color: var(--color-text);
  line-height: 1.4;
}

.subtask-status {
  color: var(--color-text-muted);
  font-size: 13px;
}

.subtask-row--done .subtask-title {
  color: var(--color-text-muted);
  text-decoration: line-through;
}
</style>
