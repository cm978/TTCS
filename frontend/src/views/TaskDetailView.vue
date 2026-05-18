<template>
  <AppLayout>
    <section class="task-detail-view">
      <a-skeleton v-if="taskStore.loading" active :paragraph="{ rows: 8 }" />
      <a-alert v-else-if="taskStore.error" type="error" show-icon>
        <template #message>{{ taskStore.error }}</template>
      </a-alert>
      <template v-else-if="task">
        <header class="detail-header">
          <div>
            <p class="breadcrumb">任务 / 完整详情</p>
            <h1>{{ task.title }}</h1>
            <p>{{ statusLabel(task.status) }} · {{ typeLabel(task.task_type) }} · {{ task.participants.length }} 名参与者</p>
          </div>
          <a-button @click="goBoard">返回项目看板</a-button>
        </header>

        <div class="detail-grid">
          <section class="detail-section">
            <h2>任务概览</h2>
            <p>{{ task.description || "暂无描述" }}</p>
            <p>子任务进度：{{ task.progress }}%</p>
          </section>
          <section class="detail-section">
            <h2>子任务</h2>
            <p v-if="task.subtasks.length === 0">暂无子任务</p>
            <ul v-else>
              <li v-for="subtask in task.subtasks" :key="subtask.id">{{ subtask.is_completed ? "已完成" : "未完成" }} · {{ subtask.title }}</li>
            </ul>
          </section>
          <section class="detail-section">
            <h2>工作日志历史</h2>
            <p v-if="task.work_logs.length === 0">还没有工作日志</p>
            <article v-for="log in task.work_logs" v-else :key="log.id" class="log-row">
              <strong>{{ log.work_date }} · {{ log.hours }}h · {{ log.work_type }}</strong>
              <p>{{ log.content }}</p>
            </article>
          </section>
          <section class="detail-section">
            <BlockerTimeline :logs="task.work_logs" />
          </section>
        </div>
      </template>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import BlockerTimeline from "../components/task/BlockerTimeline.vue";
import AppLayout from "../layouts/AppLayout.vue";
import { useTaskStore } from "../stores/task";
import type { TaskStatus, TaskType } from "../types/task";

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();
const taskId = computed(() => Number(route.params.taskId));
const task = computed(() => taskStore.activeTask);

function statusLabel(status: TaskStatus) {
  return { TODO: "待办", IN_PROGRESS: "进行中", IN_REVIEW: "待验收", REJECTED: "打回修改", DONE: "已完成", CLOSED: "已关闭", DELETED: "已删除" }[status];
}

function typeLabel(type: TaskType) {
  return { GENERAL: "普通", DOCUMENT: "文档", CODE: "代码" }[type];
}

function loadTask() {
  void taskStore.loadTaskDetail(taskId.value);
}

function goBoard() {
  if (task.value) {
    void router.push({ name: "project-board", params: { projectId: task.value.project_id } });
  }
}

onMounted(loadTask);
watch(taskId, loadTask);
</script>

<style scoped>
.task-detail-view {
  max-width: 1180px;
  margin: 0 auto;
}

.detail-header,
.detail-section {
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.breadcrumb {
  margin: 0 0 6px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 650;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  color: var(--color-text);
  font-size: 28px;
}

.detail-header p,
.detail-section p,
li {
  color: var(--color-text-muted);
  line-height: 1.6;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.45fr);
  gap: 16px;
}

.detail-section,
.log-row {
  display: grid;
  gap: 10px;
}

.log-row {
  padding: 12px 0;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 900px) {
  .detail-header,
  .detail-grid {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
