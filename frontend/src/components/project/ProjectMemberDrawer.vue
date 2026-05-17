<template>
  <a-drawer :open="open" title="项目成员" width="480" @close="emit('update:open', false)">
    <a-alert v-if="!isManager" type="info" show-icon class="drawer-alert">
      <template #message>只有项目经理可以管理项目成员。</template>
    </a-alert>

    <section class="add-member">
      <h3>添加项目成员</h3>
      <div class="add-member__controls">
        <a-select v-model:value="selectedUserId" :disabled="!isManager || availableTeamMembers.length === 0" placeholder="选择团队成员">
          <a-select-option v-for="member in availableTeamMembers" :key="member.user.id" :value="member.user.id">
            {{ member.user.display_name || member.user.email }}
          </a-select-option>
        </a-select>
        <a-select v-model:value="selectedRole" :disabled="!isManager">
          <a-select-option value="PROJECT_MANAGER">项目经理</a-select-option>
          <a-select-option value="PROJECT_MEMBER">项目成员</a-select-option>
        </a-select>
        <a-button type="primary" :disabled="!isManager || !selectedUserId" @click="handleAdd">添加项目成员</a-button>
      </div>
    </section>

    <div class="member-list">
      <article v-for="member in members" :key="member.id" class="member-row">
        <div>
          <strong>{{ member.user.display_name || member.user.email }}</strong>
          <p>{{ member.user.email }}</p>
          <p v-if="isLastManager(member)" class="guard-copy">项目至少需要保留 1 名项目经理。</p>
        </div>
        <div class="member-row__actions">
          <a-select
            :value="member.role"
            :disabled="!isManager || isLastManager(member)"
            @change="(role: unknown) => emit('role-change', member, role as ProjectRole)"
          >
            <a-select-option value="PROJECT_MANAGER">项目经理</a-select-option>
            <a-select-option value="PROJECT_MEMBER">项目成员</a-select-option>
          </a-select>
          <a-popconfirm
            title="移除成员：移除后该成员将无法继续访问对应项目。"
            ok-text="移除"
            cancel-text="取消"
            :disabled="!isManager || isLastManager(member)"
            @confirm="emit('remove', member)"
          >
            <a-button danger :disabled="!isManager || isLastManager(member)">移除</a-button>
          </a-popconfirm>
        </div>
      </article>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { ProjectMember, ProjectRole } from "../../types/project";
import type { TeamMember } from "../../types/team";

const props = defineProps<{
  open: boolean;
  members: ProjectMember[];
  teamMembers: TeamMember[];
  currentUserId: number | null;
}>();

const emit = defineEmits<{
  "update:open": [value: boolean];
  add: [userId: number, role: ProjectRole];
  "role-change": [member: ProjectMember, role: ProjectRole];
  remove: [member: ProjectMember];
}>();

const selectedUserId = ref<number | null>(null);
const selectedRole = ref<ProjectRole>("PROJECT_MEMBER");
const isManager = computed(
  () =>
    props.currentUserId !== null &&
    props.members.some((member) => member.user.id === props.currentUserId && member.role === "PROJECT_MANAGER")
);
const availableTeamMembers = computed(() =>
  props.teamMembers.filter((teamMember) => !props.members.some((member) => member.user.id === teamMember.user.id))
);

function managerCount() {
  return props.members.filter((member) => member.role === "PROJECT_MANAGER").length;
}

function isLastManager(member: ProjectMember) {
  return member.role === "PROJECT_MANAGER" && managerCount() <= 1;
}

function handleAdd() {
  if (selectedUserId.value === null) {
    return;
  }
  emit("add", selectedUserId.value, selectedRole.value);
}

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      selectedUserId.value = null;
      selectedRole.value = "PROJECT_MEMBER";
    }
  }
);
</script>

<style scoped>
.drawer-alert,
.add-member {
  margin-bottom: 16px;
}

.add-member h3 {
  margin: 0 0 12px;
  color: var(--color-text);
  font-size: 16px;
}

.add-member__controls,
.member-list {
  display: grid;
  gap: 10px;
}

.member-row {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
}

.member-row strong,
.member-row p {
  margin: 0;
}

.member-row p {
  color: var(--color-text-muted);
  font-size: 14px;
}

.member-row__actions {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
}

.guard-copy {
  color: var(--color-warning) !important;
}
</style>
