<template>
  <AppLayout>
    <section class="project-board-view">
      <a-skeleton v-if="projectStore.loading" active :paragraph="{ rows: 6 }" />
      <a-alert v-else-if="projectStore.error" type="error" show-icon>
        <template #message>{{ projectStore.error }}</template>
      </a-alert>
      <template v-else-if="board">
        <header class="board-header">
          <div>
            <p class="breadcrumb">项目 / 基础看板</p>
            <h1>{{ board.project.name }}</h1>
            <p>{{ board.members.length }} 名项目成员 · {{ managerCount }} 名项目经理</p>
          </div>
          <div class="board-actions">
            <RouterLink :to="{ name: 'project-detail', params: { projectId } }"><a-button>项目详情</a-button></RouterLink>
            <RouterLink :to="{ name: 'team-detail', params: { teamId: board.project.team_id } }"><a-button>团队详情</a-button></RouterLink>
            <a-button :icon="h(UsersRound, { size: 16 })" @click="memberDrawerOpen = true">管理成员</a-button>
            <a-button type="primary" @click="createDrawerOpen = true">创建任务</a-button>
          </div>
        </header>

        <div class="board-scroll" aria-label="项目基础看板">
          <BoardColumn
            v-for="column in orderedColumns"
            :key="column.id"
            :column="column"
            :tasks="tasksByStatus(column.status)"
            @open-task="handleOpenTask"
          />
        </div>

        <ProjectMemberDrawer
          v-model:open="memberDrawerOpen"
          :members="board.members"
          :team-members="teamMembers"
          :current-user-id="auth.user?.id ?? null"
          @add="handleAddMember"
          @role-change="handleRoleChange"
          @remove="handleRemoveMember"
        />
        <TaskDrawer
          ref="taskDrawerRef"
          :open="taskStore.drawerTaskId !== null"
          :task="taskStore.activeTask"
          :loading="taskStore.loading"
          :saving="taskStore.saving"
          :error="taskStore.error"
          @update:open="(open) => !open && taskStore.closeDrawer()"
          @save-basics="handleSaveTask"
          @add-subtask="handleAddSubtask"
          @toggle-subtask="handleToggleSubtask"
          @create-work-log="handleCreateWorkLog"
          @resolve-blocker="handleResolveBlocker"
        />
        <CreateTaskDrawer
          v-model:open="createDrawerOpen"
          :saving="taskStore.saving"
          :owner-id="auth.user?.id ?? null"
          :error="createError"
          @submit="handleCreateTask"
        />
      </template>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { UsersRound } from "lucide-vue-next";
import { computed, h, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import BoardColumn from "../components/project/BoardColumn.vue";
import ProjectMemberDrawer from "../components/project/ProjectMemberDrawer.vue";
import CreateTaskDrawer from "../components/task/CreateTaskDrawer.vue";
import TaskDrawer from "../components/task/TaskDrawer.vue";
import AppLayout from "../layouts/AppLayout.vue";
import { useAuthStore } from "../stores/auth";
import { useProjectStore } from "../stores/project";
import { useTaskStore } from "../stores/task";
import { useTeamStore } from "../stores/team";
import type { BoardColumnStatus } from "../types/project";
import type { ProjectMember, ProjectRole } from "../types/project";
import type { Subtask, TaskBoardCard, TaskCreatePayload, TaskUpdatePayload, WorkLogCreatePayload } from "../types/task";

const route = useRoute();
const auth = useAuthStore();
const projectStore = useProjectStore();
const taskStore = useTaskStore();
const teamStore = useTeamStore();
const memberDrawerOpen = ref(false);
const createDrawerOpen = ref(false);
const createError = ref<string | null>(null);
const taskDrawerRef = ref<{ setMessage: (type: "success" | "error", text: string) => void } | null>(null);
const projectId = computed(() => Number(route.params.projectId));
const board = computed(() => projectStore.activeBoard);
const statusOrder: BoardColumnStatus[] = ["TODO", "IN_PROGRESS", "IN_REVIEW", "REJECTED", "DONE"];
const orderedColumns = computed(() =>
  [...(board.value?.columns ?? [])].sort((a, b) => statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status))
);
const managerCount = computed(
  () => board.value?.members.filter((member) => member.role === "PROJECT_MANAGER").length ?? 0
);
const teamMembers = computed(() => (board.value ? teamStore.membersByTeam[board.value.project.team_id] ?? [] : []));

async function loadBoard() {
  const loaded = await projectStore.loadBoard(projectId.value);
  await teamStore.loadTeamMembers(loaded.project.team_id);
  await taskStore.loadProjectTasks(projectId.value);
}

async function refreshBoard() {
  await projectStore.loadBoard(projectId.value);
}

async function handleAddMember(userId: number, role: ProjectRole) {
  await projectStore.addMember(projectId.value, { user_id: userId, role });
  await refreshBoard();
}

async function handleRoleChange(member: ProjectMember, role: ProjectRole) {
  await projectStore.updateMemberRole(projectId.value, member.user.id, { role });
  await refreshBoard();
}

async function handleRemoveMember(member: ProjectMember) {
  await projectStore.removeMember(projectId.value, member.user.id);
  await refreshBoard();
}

function tasksByStatus(status: BoardColumnStatus) {
  return taskStore.tasksByStatus(projectId.value, status);
}

async function handleOpenTask(task: TaskBoardCard) {
  taskStore.openDrawer(task.id);
  await taskStore.loadTaskDetail(task.id);
}

async function handleCreateTask(payload: TaskCreatePayload) {
  createError.value = null;
  if (!auth.user) {
    createError.value = "请先登录后再创建任务。";
    return;
  }
  try {
    const task = await taskStore.createTask(projectId.value, payload);
    createDrawerOpen.value = false;
    taskStore.openDrawer(task.id);
    taskDrawerRef.value?.setMessage("success", "任务已创建。");
  } catch (error) {
    createError.value = error instanceof Error ? error.message : "任务创建失败，请稍后重试。";
  }
}

async function handleSaveTask(payload: TaskUpdatePayload) {
  if (taskStore.activeTask) {
    try {
      await taskStore.updateTask(taskStore.activeTask.id, payload);
      taskDrawerRef.value?.setMessage("success", "任务已保存。");
    } catch (error) {
      taskDrawerRef.value?.setMessage("error", error instanceof Error ? error.message : "任务保存失败。");
    }
  }
}

async function handleAddSubtask(title: string) {
  if (taskStore.activeTask) {
    await taskStore.addSubtask(taskStore.activeTask.id, title);
  }
}

async function handleToggleSubtask(subtask: Subtask, isCompleted: boolean) {
  if (taskStore.activeTask) {
    try {
      await taskStore.toggleSubtask(taskStore.activeTask.id, subtask, isCompleted);
      taskDrawerRef.value?.setMessage("success", isCompleted ? "子任务已完成。" : "子任务已取消完成。");
    } catch (error) {
      taskDrawerRef.value?.setMessage("error", error instanceof Error ? error.message : "子任务状态更新失败。");
    }
  }
}

async function handleCreateWorkLog(payload: WorkLogCreatePayload) {
  if (taskStore.activeTask) {
    try {
      await taskStore.createWorkLog(taskStore.activeTask.id, payload);
      taskDrawerRef.value?.setMessage("success", payload.is_blocked ? "任务已标记阻塞。" : "工作日志已保存。");
    } catch (error) {
      taskDrawerRef.value?.setMessage("error", error instanceof Error ? error.message : "工作日志保存失败。");
    }
  }
}

async function handleResolveBlocker(logId: number, note: string) {
  if (taskStore.activeTask) {
    try {
      await taskStore.resolveBlocker(taskStore.activeTask.id, logId, { resolution_note: note });
      taskDrawerRef.value?.setMessage("success", "阻塞已解除。");
    } catch (error) {
      taskDrawerRef.value?.setMessage("error", error instanceof Error ? error.message : "解除阻塞失败。");
    }
  }
}

onMounted(() => {
  void loadBoard();
});

watch(projectId, () => {
  void loadBoard();
});
</script>

<style scoped>
.project-board-view {
  max-width: 1180px;
  margin: 0 auto;
}

.board-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.board-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb {
  margin: 0 0 6px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 650;
}

.board-header h1 {
  margin: 0 0 8px;
  color: var(--color-text);
  font-size: 28px;
  line-height: 1.2;
}

.board-header p {
  margin: 0;
  color: var(--color-text-muted);
}

.board-scroll {
  display: grid;
  grid-template-columns: repeat(5, minmax(220px, 1fr));
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}

@media (max-width: 900px) {
  .board-header {
    display: grid;
  }
}
</style>
