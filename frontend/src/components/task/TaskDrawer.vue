<template>
  <a-drawer :open="open" width="640" @close="emit('update:open', false)">
    <template #title>
      <span class="drawer-title">{{ task?.title || "任务详情" }}</span>
    </template>
    <a-skeleton v-if="loading" active :paragraph="{ rows: 8 }" />
    <a-alert v-else-if="error" type="error" show-icon>
      <template #message>{{ error }}</template>
    </a-alert>
    <div v-else-if="task" class="task-drawer">
      <div class="chip-row">
        <a-tag>{{ statusLabel(task.status) }}</a-tag>
        <a-tag>{{ typeLabel(task.task_type) }}</a-tag>
        <a-tag v-if="task.is_blocked" color="warning">阻塞中</a-tag>
      </div>

      <a-form layout="vertical" @finish="handleSaveBasics">
        <a-form-item label="任务标题" required>
          <a-input v-model:value="basicForm.title" />
        </a-form-item>
        <a-form-item label="任务描述">
          <a-textarea v-model:value="basicForm.description" :rows="3" />
        </a-form-item>
        <div class="form-grid">
          <a-form-item label="任务类型">
            <a-select v-model:value="basicForm.task_type">
              <a-select-option value="GENERAL">普通</a-select-option>
              <a-select-option value="DOCUMENT">文档</a-select-option>
              <a-select-option value="CODE">代码</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="优先级">
            <a-select v-model:value="basicForm.priority">
              <a-select-option value="URGENT">紧急</a-select-option>
              <a-select-option value="HIGH">高</a-select-option>
              <a-select-option value="MEDIUM">中</a-select-option>
              <a-select-option value="LOW">低</a-select-option>
            </a-select>
          </a-form-item>
        </div>
        <p class="helper">每个任务最多 5 名参与者，Owner 会自动计入。</p>
        <a-button type="primary" html-type="submit" :loading="saving">保存任务</a-button>
      </a-form>

      <SubtaskChecklist :subtasks="task.subtasks" @add="emit('add-subtask', $event)" @toggle="handleToggleSubtask" />

      <section class="drawer-section">
        <h3>记录工作日志</h3>
        <WorkLogForm :saving="saving" @submit="emit('create-work-log', $event)" />
      </section>

      <section v-if="unresolvedBlockers.length" class="drawer-section">
        <h3>解除阻塞</h3>
        <p class="helper">存在未解除阻塞时，任务后续不能提交验收。</p>
        <article v-for="log in unresolvedBlockers" :key="log.id" class="blocker-row">
          <strong>{{ log.blocked_reason }}</strong>
          <a-textarea v-model:value="resolutionNotes[log.id]" :rows="2" placeholder="处理说明，至少 10 个字符" />
          <a-button :disabled="(resolutionNotes[log.id] || '').trim().length < 10" @click="emit('resolve-blocker', log.id, resolutionNotes[log.id])">
            解除阻塞
          </a-button>
        </article>
      </section>

      <a-button block @click="goDetail">打开完整详情</a-button>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";
import { useRouter } from "vue-router";

import type { Subtask, TaskDetail, TaskPriority, TaskStatus, TaskType, WorkLog, WorkLogCreatePayload } from "../../types/task";
import SubtaskChecklist from "./SubtaskChecklist.vue";
import WorkLogForm from "./WorkLogForm.vue";

const props = defineProps<{ open: boolean; task: TaskDetail | null; loading: boolean; saving: boolean; error: string | null }>();
const emit = defineEmits<{
  "update:open": [value: boolean];
  "save-basics": [payload: { title: string; description: string | null; task_type: TaskType; priority: TaskPriority }];
  "add-subtask": [title: string];
  "toggle-subtask": [subtask: Subtask, isCompleted: boolean];
  "create-work-log": [payload: WorkLogCreatePayload];
  "resolve-blocker": [logId: number, note: string];
}>();
const router = useRouter();
const basicForm = reactive({ title: "", description: "", task_type: "GENERAL" as TaskType, priority: "MEDIUM" as TaskPriority });
const resolutionNotes = reactive<Record<number, string>>({});
const unresolvedBlockers = computed<WorkLog[]>(() =>
  (props.task?.work_logs ?? []).filter((log) => log.is_blocked && !log.resolved_at && !log.deleted_at)
);

watch(
  () => props.task,
  (task) => {
    if (!task) {
      return;
    }
    basicForm.title = task.title;
    basicForm.description = task.description ?? "";
    basicForm.task_type = task.task_type;
    basicForm.priority = task.priority;
  },
  { immediate: true }
);

function handleSaveBasics() {
  emit("save-basics", { ...basicForm, description: basicForm.description || null });
}

function handleToggleSubtask(subtask: Subtask, isCompleted: boolean) {
  emit("toggle-subtask", subtask, isCompleted);
}

function goDetail() {
  if (props.task) {
    void router.push({ name: "task-detail", params: { taskId: props.task.id } });
  }
}

function statusLabel(status: TaskStatus) {
  return { TODO: "待办", IN_PROGRESS: "进行中", IN_REVIEW: "待验收", REJECTED: "打回修改", DONE: "已完成", CLOSED: "已关闭", DELETED: "已删除" }[status];
}

function typeLabel(type: TaskType) {
  return { GENERAL: "普通", DOCUMENT: "文档", CODE: "代码" }[type];
}
</script>

<style scoped>
.task-drawer,
.drawer-section,
.blocker-row {
  display: grid;
  gap: 16px;
}

.drawer-title {
  font-weight: 700;
}

.chip-row,
.form-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.form-grid > * {
  flex: 1 1 180px;
}

.helper {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 14px;
}

.blocker-row {
  padding: 12px;
  border: 1px solid color-mix(in srgb, var(--color-warning) 35%, var(--color-border));
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-warning) 8%, var(--color-surface));
}
</style>
