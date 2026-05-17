<template>
  <a-layout class="app-shell">
    <a-layout-sider class="app-shell__sidebar" breakpoint="lg" collapsed-width="0" width="248">
      <div class="brand">
        <ShieldCheck :size="24" aria-hidden="true" />
        <span>TTCS</span>
      </div>
      <nav class="nav-list" aria-label="主导航">
        <RouterLink class="nav-item" active-class="nav-item--active" to="/app">
          <LayoutDashboard :size="18" aria-hidden="true" />
          <span>团队与项目</span>
        </RouterLink>
        <RouterLink
          v-if="teamMembersTarget"
          class="nav-item"
          active-class="nav-item--active"
          :to="teamMembersTarget"
        >
          <UsersRound :size="18" aria-hidden="true" />
          <span>团队成员</span>
        </RouterLink>
        <div v-else class="nav-item nav-item--disabled" aria-disabled="true">
          <UsersRound :size="18" aria-hidden="true" />
          <span>团队成员</span>
        </div>
        <RouterLink v-if="boardTarget" class="nav-item" active-class="nav-item--active" :to="boardTarget">
          <FolderKanban :size="18" aria-hidden="true" />
          <span>项目看板</span>
        </RouterLink>
        <div v-else class="nav-item nav-item--disabled" aria-disabled="true">
          <FolderKanban :size="18" aria-hidden="true" />
          <span>项目看板</span>
        </div>
      </nav>
    </a-layout-sider>

    <a-layout>
      <a-layout-header class="app-shell__header">
        <div class="header-title">任务可追溯协作系统</div>
        <div class="user-area">
          <div class="user-chip" aria-label="当前用户">
            <CircleUserRound :size="18" aria-hidden="true" />
            <span>{{ userLabel }}</span>
          </div>
          <a-button danger class="logout-button" :icon="h(LogOut, { size: 16 })" @click="handleLogout">
            退出登录
          </a-button>
        </div>
      </a-layout-header>
      <a-layout-content class="app-shell__content">
        <slot />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { CircleUserRound, FolderKanban, LayoutDashboard, LogOut, ShieldCheck, UsersRound } from "lucide-vue-next";
import { computed, h } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";
import { useProjectStore } from "../stores/project";
import { useTeamStore } from "../stores/team";

const auth = useAuthStore();
const teamStore = useTeamStore();
const projectStore = useProjectStore();
const router = useRouter();
const userLabel = computed(() => auth.user?.display_name || auth.user?.email || "未登录");
const teamMembersTarget = computed(() =>
  teamStore.selectedTeamId ? { name: "team-members", params: { teamId: teamStore.selectedTeamId } } : null
);
const boardTarget = computed(() => {
  const projectId = projectStore.activeBoard?.project.id ?? projectStore.projects[0]?.id;
  return projectId ? { name: "project-board", params: { projectId } } : null;
});

function handleLogout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.app-shell {
  min-height: 100dvh;
  background: var(--color-bg);
}

.app-shell__sidebar {
  background: #111827 !important;
}

.brand {
  min-height: 64px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  color: #ffffff;
  font-size: 20px;
  font-weight: 700;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

.nav-item {
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  color: rgba(255, 255, 255, 0.78);
  text-decoration: none;
}

.nav-item--active {
  background: rgba(37, 99, 235, 0.22);
  color: #ffffff;
}

.nav-item--disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.app-shell__header {
  height: auto;
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 24px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  line-height: 1.4;
}

.header-title {
  font-weight: 650;
  color: var(--color-text);
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.user-chip {
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  background: var(--color-surface-raised);
}

.logout-button {
  min-height: 44px;
}

.app-shell__content {
  padding: 24px;
}

@media (max-width: 767px) {
  .app-shell__header {
    align-items: flex-start;
    padding: 12px 16px;
  }

  .app-shell__content {
    padding: 16px;
  }
}
</style>
