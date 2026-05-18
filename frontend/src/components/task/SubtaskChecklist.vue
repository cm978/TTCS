<template>
  <section class="subtask-checklist">
    <header>
      <h3>子任务</h3>
      <span>{{ completed }}/{{ subtasks.length }} 已完成</span>
    </header>
    <div v-if="subtasks.length === 0" class="empty">暂无子任务</div>
    <label v-for="subtask in subtasks" :key="subtask.id" class="subtask-row">
      <a-checkbox :checked="subtask.is_completed" @change="emit('toggle', subtask, !subtask.is_completed)" />
      <span>{{ subtask.title }}</span>
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

const props = defineProps<{ subtasks: Subtask[] }>();
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
</script>

<style scoped>
.subtask-checklist {
  display: grid;
  gap: 10px;
}

header,
.subtask-row,
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
  justify-content: flex-start;
  min-height: 36px;
}
</style>
