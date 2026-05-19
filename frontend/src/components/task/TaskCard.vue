<template>
  <button class="task-card" type="button" @click="emit('open', task)">
    <span v-if="isBlocked" class="blocker-chip"><AlertTriangle :size="14" /> 阻塞中</span>
    <span class="task-title">{{ task.title }}</span>
    <span class="task-meta">
      <span>{{ typeLabel(task.task_type) }}</span>
      <span :class="['priority', `priority--${task.priority.toLowerCase()}`]">{{ priorityLabel(task.priority) }}</span>
    </span>
    <span class="task-meta">
      <span><UserRound :size="14" /> {{ task.owner?.display_name || task.owner?.email || "未命名 Owner" }}</span>
      <span>{{ participantLabel }}</span>
    </span>
    <span class="task-meta">
      <span><CalendarDays :size="14" /> {{ task.due_date || "未设置截止日期" }}</span>
      <span>{{ task.subtask_completed }}/{{ task.subtask_total }} 子任务</span>
    </span>
    <span class="task-footer">
      <span><Clock3 :size="14" /> {{ logState }}</span>
      <span v-if="task.progress > 0">{{ task.progress }}%</span>
    </span>
  </button>
</template>

<script setup lang="ts">
import { AlertTriangle, CalendarDays, Clock3, UserRound } from "lucide-vue-next";
import { computed } from "vue";

import type { TaskBoardCard, TaskPriority, TaskType } from "../../types/task";

const props = defineProps<{ task: TaskBoardCard }>();
const emit = defineEmits<{ open: [task: TaskBoardCard] }>();

const isBlocked = computed(() => props.task.blocker_summary?.is_blocked || props.task.is_blocked);
const participantLabel = computed(() => {
  const names = props.task.participants
    .map((participant) => participant.user?.display_name || participant.user?.email)
    .filter(Boolean) as string[];
  if (names.length === 0) {
    return "暂无参与者";
  }
  const visible = names.slice(0, 2).join("、");
  return names.length > 2 ? `${visible} 等 ${names.length} 人` : visible;
});
const logState = computed(() => {
  if (!props.task.latest_work_log_at) {
    return "待写日志";
  }
  const today = new Date().toISOString().slice(0, 10);
  return props.task.latest_work_log_at.startsWith(today) ? "今日已写日志" : "已有日志";
});

function typeLabel(type: TaskType) {
  return { GENERAL: "普通", DOCUMENT: "文档", CODE: "代码" }[type];
}

function priorityLabel(priority: TaskPriority) {
  return { URGENT: "紧急", HIGH: "高", MEDIUM: "中", LOW: "低" }[priority];
}
</script>

<style scoped>
.task-card {
  width: 100%;
  display: grid;
  gap: 8px;
  padding: 14px;
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
  transition: border-color 180ms ease, transform 180ms ease;
}

.task-card:hover,
.task-card:focus-visible {
  border-color: var(--color-primary);
  transform: translateY(-1px);
}

.blocker-chip {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid color-mix(in srgb, var(--color-warning) 40%, var(--color-border));
  border-radius: var(--radius-sm);
  color: var(--color-warning);
  background: color-mix(in srgb, var(--color-warning) 10%, var(--color-surface));
  font-size: 13px;
  font-weight: 650;
}

.task-title {
  color: var(--color-text);
  font-size: 15px;
  font-weight: 650;
  line-height: 1.35;
}

.task-meta,
.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: var(--color-text-muted);
  font-size: 13px;
  line-height: 1.4;
}

.task-meta span,
.task-footer span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}

.priority {
  font-weight: 650;
}

.priority--urgent,
.priority--high {
  color: var(--color-danger);
}
</style>
