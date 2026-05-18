<template>
  <a-drawer :open="open" width="560" @close="handleClose">
    <template #title>创建任务</template>
    <a-alert v-if="error" class="form-alert" type="error" show-icon>
      <template #message>{{ error }}</template>
    </a-alert>
    <a-form layout="vertical" class="create-task-form" @finish="handleSubmit">
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
      <a-form-item label="截止日期">
        <a-date-picker v-model:value="dueDate" :disabled-date="disablePastDate" />
      </a-form-item>
      <footer class="drawer-actions">
        <a-button @click="handleClose">取消</a-button>
        <a-button type="primary" html-type="submit" :loading="saving" :disabled="form.title.trim().length < 2">确认创建</a-button>
      </footer>
    </a-form>
  </a-drawer>
</template>

<script setup lang="ts">
import dayjs, { type Dayjs } from "dayjs";
import { reactive, ref, watch } from "vue";

import type { TaskCreatePayload, TaskPriority, TaskType } from "../../types/task";

const props = defineProps<{ open: boolean; saving: boolean; ownerId: number | null; error: string | null }>();
const emit = defineEmits<{ "update:open": [value: boolean]; submit: [payload: TaskCreatePayload] }>();

const dueDate = ref<Dayjs | null>(null);
const form = reactive({
  title: "",
  description: "",
  task_type: "GENERAL" as TaskType,
  priority: "MEDIUM" as TaskPriority
});

watch(
  () => props.open,
  (open) => {
    if (!open) {
      resetForm();
    }
  }
);

function disablePastDate(current: Dayjs) {
  return current && current.isBefore(dayjs(), "day");
}

function resetForm() {
  form.title = "";
  form.description = "";
  form.task_type = "GENERAL";
  form.priority = "MEDIUM";
  dueDate.value = null;
}

function handleClose() {
  emit("update:open", false);
}

function handleSubmit() {
  const title = form.title.trim();
  if (!props.ownerId || title.length < 2) {
    return;
  }
  emit("submit", {
    title,
    description: form.description.trim() || null,
    owner_id: props.ownerId,
    participant_ids: [],
    task_type: form.task_type,
    priority: form.priority,
    due_date: dueDate.value ? dueDate.value.format("YYYY-MM-DD") : null
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
</style>
