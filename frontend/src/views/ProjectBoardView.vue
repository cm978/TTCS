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
          <a-button type="primary" :icon="h(UsersRound, { size: 16 })" @click="memberDrawerOpen = true">
            管理成员
          </a-button>
        </header>

        <div class="board-scroll" aria-label="项目基础看板">
          <BoardColumn v-for="column in orderedColumns" :key="column.id" :column="column" />
        </div>
      </template>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { UsersRound } from "lucide-vue-next";
import { computed, h, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import BoardColumn from "../components/project/BoardColumn.vue";
import AppLayout from "../layouts/AppLayout.vue";
import { useProjectStore } from "../stores/project";
import type { BoardColumnStatus } from "../types/project";

const route = useRoute();
const projectStore = useProjectStore();
const memberDrawerOpen = ref(false);
const projectId = computed(() => Number(route.params.projectId));
const board = computed(() => projectStore.activeBoard);
const statusOrder: BoardColumnStatus[] = ["TODO", "IN_PROGRESS", "IN_REVIEW", "REJECTED", "DONE"];
const orderedColumns = computed(() =>
  [...(board.value?.columns ?? [])].sort((a, b) => statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status))
);
const managerCount = computed(
  () => board.value?.members.filter((member) => member.role === "PROJECT_MANAGER").length ?? 0
);

async function loadBoard() {
  await projectStore.loadBoard(projectId.value);
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
