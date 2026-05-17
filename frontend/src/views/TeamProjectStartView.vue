<template>
  <AppLayout>
    <section class="start-view">
      <header class="page-header">
        <div>
          <p class="eyebrow">Phase 2</p>
          <h1>团队与项目</h1>
          <p>团队承载成员协作，项目进入基础看板工作区。</p>
        </div>
        <a-button type="primary" :icon="h(Plus, { size: 16 })" @click="showCreateTeam = true">创建团队</a-button>
      </header>

      <a-alert v-if="teamStore.error || projectStore.error" type="error" show-icon class="state-alert">
        <template #message>{{ teamStore.error || projectStore.error }}</template>
        <template #description>
          <a-button size="small" @click="refresh">重试</a-button>
        </template>
      </a-alert>

      <a-skeleton v-if="teamStore.loading || projectStore.loading" active :paragraph="{ rows: 5 }" />

      <template v-else>
        <section v-if="teamStore.myInvitations.length" class="panel invitation-panel">
          <div>
            <h2>你有待接受的团队邀请</h2>
            <p>接受后会按邀请角色加入团队。</p>
          </div>
          <ul class="invitation-list">
            <li v-for="invitation in teamStore.myInvitations" :key="invitation.id">
              <span>{{ invitation.email }}</span>
              <a-tag color="blue">{{ roleLabel(invitation.role) }}</a-tag>
              <a-button type="primary" size="small" @click="handleAcceptInvitation(invitation.id)">接受邀请</a-button>
            </li>
          </ul>
        </section>

        <section v-if="!teamStore.hasTeams" class="panel empty-panel">
          <UsersRound :size="32" aria-hidden="true" />
          <h2>还没有团队</h2>
          <p>创建团队后，你可以邀请成员并创建第一个项目看板。</p>
          <a-button type="primary" size="large" :icon="h(Plus, { size: 16 })" @click="showCreateTeam = true">
            创建第一个团队
          </a-button>
        </section>

        <div v-else class="workspace-grid">
          <section class="panel">
            <div class="section-heading">
              <h2>团队</h2>
              <span>{{ teamStore.teams.length }} 个团队</span>
            </div>
            <div class="selection-list">
              <button
                v-for="team in teamStore.teams"
                :key="team.id"
                class="selection-row"
                :class="{ 'selection-row--active': team.id === teamStore.selectedTeamId }"
                type="button"
                @click="selectTeam(team.id)"
              >
                <span>{{ team.name }}</span>
                <RouterLink :to="{ name: 'team-members', params: { teamId: team.id } }">成员管理</RouterLink>
              </button>
            </div>
          </section>

          <section class="panel">
            <div class="section-heading">
              <h2>项目</h2>
              <span>{{ visibleProjects.length }} 个项目</span>
            </div>
            <a-empty v-if="visibleProjects.length === 0" description="当前团队还没有项目。" />
            <div v-else class="project-list">
              <RouterLink
                v-for="project in visibleProjects"
                :key="project.id"
                class="project-row"
                :to="{ name: 'project-board', params: { projectId: project.id } }"
              >
                <FolderKanban :size="18" aria-hidden="true" />
                <span>{{ project.name }}</span>
              </RouterLink>
            </div>
          </section>
        </div>
      </template>

      <a-modal v-model:open="showCreateTeam" title="创建团队" :footer="null">
        <a-form layout="vertical" @finish="handleCreateTeam">
          <a-form-item label="团队名称" name="name" extra="2-50 个字符，团队名称需唯一" required>
            <a-input v-model:value="teamForm.name" />
          </a-form-item>
          <a-form-item label="团队描述" name="description" extra="最多 500 个字符">
            <a-textarea v-model:value="teamForm.description" :rows="3" />
          </a-form-item>
          <div class="modal-actions">
            <a-button @click="showCreateTeam = false">取消</a-button>
            <a-button type="primary" html-type="submit" :loading="teamStore.loading">创建团队</a-button>
          </div>
        </a-form>
      </a-modal>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { FolderKanban, Plus, UsersRound } from "lucide-vue-next";
import { computed, h, onMounted, reactive, ref } from "vue";

import AppLayout from "../layouts/AppLayout.vue";
import { useProjectStore } from "../stores/project";
import { useTeamStore } from "../stores/team";
import type { TeamRole } from "../types/team";

const teamStore = useTeamStore();
const projectStore = useProjectStore();
const showCreateTeam = ref(false);
const teamForm = reactive({ name: "", description: "" });

const visibleProjects = computed(() => {
  if (!teamStore.selectedTeamId) {
    return projectStore.projects;
  }
  return projectStore.projects.filter((project) => project.team_id === teamStore.selectedTeamId);
});

function roleLabel(role: TeamRole) {
  return role === "TEAM_ADMIN" ? "管理员" : "成员";
}

async function refresh() {
  await teamStore.loadAppData();
  await projectStore.loadProjects();
}

async function selectTeam(teamId: number) {
  teamStore.selectedTeamId = teamId;
  await projectStore.loadProjects(teamId);
}

async function handleCreateTeam() {
  const team = await teamStore.createTeam({ name: teamForm.name, description: teamForm.description || null });
  teamForm.name = "";
  teamForm.description = "";
  showCreateTeam.value = false;
  await selectTeam(team.id);
}

async function handleAcceptInvitation(invitationId: number) {
  await teamStore.acceptInvitation(invitationId);
  await projectStore.loadProjects();
}

onMounted(() => {
  void refresh();
});
</script>

<style scoped>
.start-view {
  max-width: 1180px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 650;
}

.page-header h1,
.panel h2 {
  margin: 0;
  color: var(--color-text);
}

.page-header h1 {
  font-size: 28px;
  line-height: 1.2;
}

.page-header p,
.panel p {
  margin: 8px 0 0;
  color: var(--color-text-muted);
}

.state-alert {
  margin-bottom: 16px;
}

.panel {
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.invitation-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 1.4fr);
  gap: 16px;
  margin-bottom: 16px;
}

.invitation-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.invitation-list li,
.selection-row,
.project-row {
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
}

.invitation-list li {
  justify-content: space-between;
  padding: 8px 12px;
}

.empty-panel {
  display: grid;
  justify-items: start;
  gap: 12px;
}

.empty-panel svg {
  color: var(--color-primary);
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.8fr) minmax(0, 1.2fr);
  gap: 16px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

.selection-list,
.project-list {
  display: grid;
  gap: 10px;
}

.selection-row {
  width: 100%;
  justify-content: space-between;
  padding: 0 12px;
  color: var(--color-text);
  cursor: pointer;
}

.selection-row--active {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.project-row {
  padding: 0 12px;
  color: var(--color-text);
  text-decoration: none;
}

.project-row svg {
  color: var(--color-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 900px) {
  .page-header,
  .invitation-panel,
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    display: grid;
  }
}
</style>
