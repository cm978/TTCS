<template>
  <a-drawer :open="open" width="560" @close="handleClose">
    <template #title>创建任务</template>
    <a-alert v-if="error" class="form-alert" type="error" show-icon>
      <template #message>{{ error }}</template>
    </a-alert>
    <div class="create-task-form">
      <a-form-item label="任务标题" required>
        <a-input v-model:value="form.title" placeholder="输入任务标题" />
      </a-form-item>
      <a-form-item label="任务描述">
        <a-textarea v-model:value="form.description" :rows="3" placeholder="说明任务目标、交付物或注意事项" />
      </a-form-item>
      <div class="form-grid">
        <a-form-item label="任务类型">
          <a-select v-model:value="form.task_type">
            <a-select-option value="GENERAL">普通</a-select-option>
            <a-select-option value="DOCUMENT">文档</a-select-option>
            <a-select-option value="CODE">代码</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="优先级">
          <a-select v-model:value="form.priority">
            <a-select-option value="URGENT">紧急</a-select-option>
            <a-select-option value="HIGH">高</a-select-option>
            <a-select-option value="MEDIUM">中</a-select-option>
            <a-select-option value="LOW">低</a-select-option>
          </a-select>
        </a-form-item>
      </div>
      <div class="form-grid">
        <label class="field">
          <span>开始日期</span>
          <input v-model="form.start_date" class="native-input" type="date" />
        </label>
        <label class="field">
          <span>截止日期</span>
          <input v-model="form.due_date" class="native-input" type="date" />
        </label>
      </div>
      <p v-if="localError" class="form-error">{{ localError }}</p>
      <footer class="drawer-actions">
        <a-button @click="handleClose">取消</a-button>
        <a-button type="primary" :loading="saving" :disabled="form.title.trim().length < 2" @click="handleSubmit">确认创建</a-button>
      </footer>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";

import type { TaskCreatePayload, TaskPriority, TaskType } from "../../types/task";

const props = defineProps<{ open: boolean; saving: boolean; ownerId: number | null; error: string | null }>();
const emit = defineEmits<{ "update:open": [value: boolean]; submit: [payload: TaskCreatePayload] }>();

const localError = ref("");
const form = reactive({
  title: "",
  description: "",
  task_type: "GENERAL" as TaskType,
  priority: "MEDIUM" as TaskPriority,
  start_date: "",
  due_date: ""
});

watch(
  () => props.open,
  (open) => {
    if (!open) {
      resetForm();
    }
  }
);

function resetForm() {
  form.title = "";
  form.description = "";
  form.task_type = "GENERAL";
  form.priority = "MEDIUM";
  form.start_date = "";
  form.due_date = "";
  localError.value = "";
}

function handleClose() {
  emit("update:open", false);
}

function handleSubmit() {
  const title = form.title.trim();
  if (!props.ownerId || title.length < 2) {
    localError.value = "请至少填写 2 个字符的任务标题。";
    return;
  }
  if (form.start_date && form.due_date && form.due_date < form.start_date) {
    localError.value = "截止日期不能早于开始日期。";
    return;
  }
  localError.value = "";
  emit("submit", {
    title,
    description: form.description.trim() || null,
    owner_id: props.ownerId,
    participant_ids: [],
    task_type: form.task_type,
    priority: form.priority,
    start_date: form.start_date || null,
    due_date: form.due_date || null
  });
}
</script>

<style scoped>
.create-task-form {
  display: grid;
  gap: 4px;
}

.form-grid,
.drawer-actions {
  display: flex;
  gap: 8px;
}

.form-grid > * {
  flex: 1 1 180px;
}

.drawer-actions {
  justify-content: flex-end;
}

.form-alert {
  margin-bottom: 16px;
}

.field {
  display: grid;
  gap: 8px;
  color: var(--color-text);
  font-weight: 600;
}

.native-input {
  min-height: 40px;
  padding: 6px 11px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
}

.native-input:focus {
  border-color: var(--color-primary);
  outline: 2px solid color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.form-error {
  margin: 0;
  color: var(--color-danger);
  font-size: 14px;
}
</style>
