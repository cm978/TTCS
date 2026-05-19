<template>
  <AppLayout>
    <section class="project-detail-view">
      <a-skeleton v-if="projectStore.loading" active :paragraph="{ rows: 7 }" />
      <a-alert v-else-if="projectStore.error" type="error" show-icon>
        <template #message>{{ projectStore.error }}</template>
      </a-alert>
      <template v-else-if="board">
        <header class="detail-header">
          <div>
            <p class="breadcrumb">团队项目 / 项目详情</p>
            <h1>{{ board.project.name }}</h1>
            <p>{{ board.project.description || "暂无项目说明" }}</p>
          </div>
          <div class="header-actions">
            <RouterLink :to="{ name: 'team-detail', params: { teamId: board.project.team_id } }"><a-button>返回团队</a-button></RouterLink>
            <RouterLink :to="{ name: 'project-board', params: { projectId } }"><a-button type="primary">进入任务看板</a-button></RouterLink>
          </div>
        </header>

        <div class="summary-grid">
          <section class="metric">
            <span>项目周期</span>
            <strong>{{ dateRange(board.project.start_date, board.project.end_date) }}</strong>
          </section>
          <section class="metric">
            <span>项目成员</span>
            <strong>{{ board.members.length }} 人</strong>
          </section>
          <section class="metric">
            <span>看板列</span>
            <strong>{{ board.columns.length }} 列</strong>
          </section>
        </div>

        <section class="panel">
          <div class="section-heading">
            <h2>看板列预览</h2>
            <span>任务执行从这里进入</span>
          </div>
          <div class="column-list">
            <div v-for="column in orderedColumns" :key="column.id" class="column-row">
              <strong>{{ column.name }}</strong>
              <span>{{ statusLabel(column.status) }}</span>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="section-heading">
            <h2>项目成员</h2>
            <RouterLink :to="{ name: 'project-board', params: { projectId } }"><a-button>从看板管理成员</a-button></RouterLink>
          </div>
          <div class="member-list">
            <div v-for="member in board.members" :key="member.id" class="member-row">
              <span>{{ member.user.display_name || member.user.email }}</span>
              <a-tag>{{ member.role === "PROJECT_MANAGER" ? "项目经理" : "项目成员" }}</a-tag>
            </div>
          </div>
        </section>
      </template>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

import AppLayout from "../layouts/AppLayout.vue";
import { useProjectStore } from "../stores/project";
import type { BoardColumnStatus } from "../types/project";

const route = useRoute();
const projectStore = useProjectStore();
const projectId = computed(() => Number(route.params.projectId));
const board = computed(() => projectStore.activeBoard);
const statusOrder: BoardColumnStatus[] = ["TODO", "IN_PROGRESS", "IN_REVIEW", "REJECTED", "DONE"];
const orderedColumns = computed(() =>
  [...(board.value?.columns ?? [])].sort((a, b) => statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status))
);

function loadDetail() {
  void projectStore.loadBoard(projectId.value);
}

function dateRange(start: string | null, end: string | null) {
  if (!start && !end) {
    return "未设置";
  }
  return `${start || "未设置开始"} -> ${end || "未设置结束"}`;
}

function statusLabel(status: BoardColumnStatus) {
  return { TODO: "待办", IN_PROGRESS: "进行中", IN_REVIEW: "待验收", REJECTED: "打回修改", DONE: "已完成" }[status];
}

onMounted(loadDetail);
watch(projectId, loadDetail);
</script>

<style scoped>
.project-detail-view {
  max-width: 1180px;
  margin: 0 auto;
}

.detail-header,
.panel,
.metric {
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.detail-header,
.section-heading,
.header-actions,
.column-row,
.member-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.header-actions {
  flex-wrap: wrap;
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

p,
.section-heading span,
.column-row span,
.metric span {
  color: var(--color-text-muted);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.metric {
  display: grid;
  gap: 6px;
}

.metric strong {
  color: var(--color-text);
  font-size: 22px;
}

.panel {
  margin-top: 16px;
}

.column-list,
.member-list {
  display: grid;
  gap: 10px;
}

.column-row,
.member-row {
  min-height: 44px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
}
</style>
