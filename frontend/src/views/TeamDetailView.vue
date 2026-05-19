<template>
  <AppLayout>
    <section class="detail-view">
      <a-skeleton v-if="teamStore.loading || projectStore.loading" active :paragraph="{ rows: 6 }" />
      <a-alert v-else-if="teamStore.error || projectStore.error" type="error" show-icon>
        <template #message>{{ teamStore.error || projectStore.error }}</template>
      </a-alert>
      <template v-else-if="team">
        <header class="detail-header">
          <div>
            <p class="breadcrumb">我的团队 / 团队详情</p>
            <h1>{{ team.name }}</h1>
            <p>{{ team.description || "暂无团队说明" }}</p>
          </div>
          <div class="header-actions">
            <RouterLink :to="{ name: 'team-project-start' }"><a-button>返回团队列表</a-button></RouterLink>
            <RouterLink :to="{ name: 'team-members', params: { teamId } }"><a-button>管理成员</a-button></RouterLink>
          </div>
        </header>

        <div class="summary-grid">
          <section class="metric">
            <span>团队成员</span>
            <strong>{{ members.length }}</strong>
          </section>
          <section class="metric">
            <span>团队项目</span>
            <strong>{{ projects.length }}</strong>
          </section>
        </div>

        <section class="panel">
          <div class="section-heading">
            <h2>团队项目</h2>
            <a-button type="primary" @click="createOpen = true">创建项目</a-button>
          </div>
          <a-empty v-if="projects.length === 0" description="当前团队还没有项目。" />
          <div v-else class="project-list">
            <RouterLink v-for="project in projects" :key="project.id" class="project-row" :to="{ name: 'project-detail', params: { projectId: project.id } }">
              <div>
                <strong>{{ project.name }}</strong>
                <p>{{ project.description || "暂无项目说明" }}</p>
              </div>
              <span>{{ dateRange(project.start_date, project.end_date) }}</span>
            </RouterLink>
          </div>
        </section>

        <CreateProjectModal
          v-model:open="createOpen"
          :loading="projectStore.loading"
          :error="projectStore.error"
          :created="false"
          @submit="handleCreateProject"
        />
      </template>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import CreateProjectModal from "../components/project/CreateProjectModal.vue";
import AppLayout from "../layouts/AppLayout.vue";
import { useProjectStore } from "../stores/project";
import { useTeamStore } from "../stores/team";
import type { ProjectCreatePayload } from "../types/project";

const route = useRoute();
const router = useRouter();
const teamStore = useTeamStore();
const projectStore = useProjectStore();
const createOpen = ref(false);
const teamId = computed(() => Number(route.params.teamId));
const team = computed(() => teamStore.activeTeam ?? teamStore.teams.find((item) => item.id === teamId.value) ?? null);
const members = computed(() => teamStore.membersByTeam[teamId.value] ?? []);
const projects = computed(() => projectStore.projects.filter((project) => project.team_id === teamId.value));

async function loadDetail() {
  await teamStore.loadTeam(teamId.value);
  await Promise.all([teamStore.loadTeamMembers(teamId.value), projectStore.loadProjects(teamId.value)]);
}

async function handleCreateProject(payload: ProjectCreatePayload) {
  const project = await projectStore.createProject(teamId.value, payload);
  createOpen.value = false;
  await router.push({ name: "project-detail", params: { projectId: project.id } });
}

function dateRange(start: string | null, end: string | null) {
  if (!start && !end) {
    return "未设置周期";
  }
  return `${start || "未设置开始"} -> ${end || "未设置结束"}`;
}

onMounted(() => {
  void loadDetail();
});
watch(teamId, () => {
  void loadDetail();
});
</script>

<style scoped>
.detail-view {
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
.project-row,
.header-actions {
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
.project-row span,
.metric span {
  color: var(--color-text-muted);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(180px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.metric {
  display: grid;
  gap: 6px;
}

.metric strong {
  color: var(--color-text);
  font-size: 28px;
}

.project-list {
  display: grid;
  gap: 10px;
}

.project-row {
  min-height: 64px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  text-decoration: none;
  background: var(--color-surface-raised);
}
</style>
