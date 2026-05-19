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

      <div class="task-form">
        <a-alert v-if="actionMessage" :type="actionMessage.type" show-icon class="drawer-alert">
          <template #message>{{ actionMessage.text }}</template>
        </a-alert>
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
        <div class="form-grid">
          <label class="field">
            <span>开始日期</span>
            <input v-model="basicForm.start_date" class="native-input" type="date" />
          </label>
          <label class="field">
            <span>截止日期</span>
            <input v-model="basicForm.due_date" class="native-input" type="date" />
          </label>
        </div>
        <p class="helper">每个任务最多 5 名参与者，Owner 会自动计入。</p>
        <a-button type="primary" :loading="saving" @click="handleSaveBasics">保存任务</a-button>
      </div>

      <SubtaskChecklist
        :subtasks="task.subtasks"
        :updating-id="updatingSubtaskId"
        @add="emit('add-subtask', $event)"
        @toggle="handleToggleSubtask"
      />

      <section class="drawer-section">
        <header class="section-header">
          <div>
            <h3>工作日志</h3>
            <p class="helper">手动记录工作内容，可选填写代码引用。</p>
          </div>
          <a-button @click="workLogOpen = !workLogOpen">{{ workLogOpen ? "收起表单" : "记录工作日志" }}</a-button>
        </header>
        <WorkLogForm v-if="workLogOpen" :saving="saving" mode="log" @submit="handleWorkLogSubmit" />
      </section>

      <section class="drawer-section">
        <header class="section-header">
          <div>
            <h3>阻塞</h3>
            <p class="helper">无法推进时，单独标记阻塞并说明原因。</p>
          </div>
          <a-button @click="blockerOpen = !blockerOpen">{{ blockerOpen ? "收起表单" : "标记阻塞" }}</a-button>
        </header>
        <WorkLogForm v-if="blockerOpen" :saving="saving" mode="blocker" @submit="handleBlockerSubmit" />
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
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import type { Subtask, TaskDetail, TaskPriority, TaskStatus, TaskType, WorkLog, WorkLogCreatePayload } from "../../types/task";
import SubtaskChecklist from "./SubtaskChecklist.vue";
import WorkLogForm from "./WorkLogForm.vue";

const props = defineProps<{ open: boolean; task: TaskDetail | null; loading: boolean; saving: boolean; error: string | null }>();
const emit = defineEmits<{
  "update:open": [value: boolean];
  "save-basics": [payload: { title: string; description: string | null; task_type: TaskType; priority: TaskPriority; start_date?: string | null; due_date: string | null }];
  "add-subtask": [title: string];
  "toggle-subtask": [subtask: Subtask, isCompleted: boolean];
  "create-work-log": [payload: WorkLogCreatePayload];
  "resolve-blocker": [logId: number, note: string];
}>();
const router = useRouter();
const basicForm = reactive({
  title: "",
  description: "",
  task_type: "GENERAL" as TaskType,
  priority: "MEDIUM" as TaskPriority,
  start_date: "",
  due_date: ""
});
const resolutionNotes = reactive<Record<number, string>>({});
const workLogOpen = ref(false);
const blockerOpen = ref(false);
const updatingSubtaskId = ref<number | null>(null);
const actionMessage = ref<{ type: "success" | "error"; text: string } | null>(null);
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
    basicForm.start_date = "";
    basicForm.due_date = task.due_date ?? "";
    actionMessage.value = null;
  },
  { immediate: true }
);

function handleSaveBasics() {
  emit("save-basics", {
    ...basicForm,
    description: basicForm.description || null,
    start_date: basicForm.start_date || null,
    due_date: basicForm.due_date || null
  });
}

function handleToggleSubtask(subtask: Subtask, isCompleted: boolean) {
  updatingSubtaskId.value = subtask.id;
  emit("toggle-subtask", subtask, isCompleted);
}

function handleWorkLogSubmit(payload: WorkLogCreatePayload) {
  emit("create-work-log", payload);
  workLogOpen.value = false;
}

function handleBlockerSubmit(payload: WorkLogCreatePayload) {
  emit("create-work-log", { ...payload, is_blocked: true });
  blockerOpen.value = false;
}

function setMessage(type: "success" | "error", text: string) {
  actionMessage.value = { type, text };
  updatingSubtaskId.value = null;
}

defineExpose({ setMessage });

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
.task-form,
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

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.section-header h3 {
  margin: 0 0 4px;
}

.drawer-alert {
  margin-bottom: 8px;
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

.blocker-row {
  padding: 12px;
  border: 1px solid color-mix(in srgb, var(--color-warning) 35%, var(--color-border));
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-warning) 8%, var(--color-surface));
}
</style>
