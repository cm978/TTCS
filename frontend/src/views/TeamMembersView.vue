<template>
  <AppLayout>
    <section class="team-members-view">
      <header class="page-header">
        <div>
          <h1>团队成员</h1>
          <p>查看成员、待接受邀请和团队角色。</p>
        </div>
        <a-button type="primary" :icon="h(UserPlus, { size: 16 })" :disabled="!isAdmin" @click="inviteOpen = true">
          邀请成员
        </a-button>
      </header>

      <a-alert v-if="!isAdmin" type="info" show-icon class="state-alert">
        <template #message>只有团队管理员可以邀请、移除成员或调整角色。</template>
      </a-alert>
      <a-alert v-if="teamStore.error" type="error" show-icon class="state-alert">
        <template #message>{{ teamStore.error }}</template>
      </a-alert>

      <a-skeleton v-if="teamStore.loading" active :paragraph="{ rows: 5 }" />
      <TeamMemberTable
        v-else
        :members="members"
        :invitations="invitations"
        :is-admin="isAdmin"
        @role-change="handleRoleChange"
        @remove="handleRemove"
        @cancel-invitation="handleCancelInvitation"
      />

      <InviteMemberModal
        v-model:open="inviteOpen"
        :loading="teamStore.loading"
        :error="teamStore.error"
        @submit="handleInvite"
      />
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { UserPlus } from "lucide-vue-next";
import { computed, h, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import InviteMemberModal from "../components/team/InviteMemberModal.vue";
import TeamMemberTable from "../components/team/TeamMemberTable.vue";
import AppLayout from "../layouts/AppLayout.vue";
import { useAuthStore } from "../stores/auth";
import { useTeamStore } from "../stores/team";
import type { TeamInvitation, TeamInvitationCreatePayload, TeamMember, TeamRole } from "../types/team";

const route = useRoute();
const auth = useAuthStore();
const teamStore = useTeamStore();
const inviteOpen = ref(false);
const teamId = computed(() => Number(route.params.teamId));
const members = computed(() => teamStore.membersByTeam[teamId.value] ?? []);
const invitations = computed(() => teamStore.invitationsByTeam[teamId.value] ?? []);
const currentMember = computed(() => members.value.find((member) => member.user.id === auth.user?.id));
const isAdmin = computed(() => currentMember.value?.role === "TEAM_ADMIN");

async function refresh() {
  teamStore.selectedTeamId = teamId.value;
  await Promise.all([teamStore.loadTeamMembers(teamId.value), teamStore.loadTeamInvitations(teamId.value)]);
}

async function handleInvite(payload: TeamInvitationCreatePayload) {
  await teamStore.inviteMember(teamId.value, payload);
  inviteOpen.value = false;
  await teamStore.loadTeamInvitations(teamId.value);
}

async function handleRoleChange(member: TeamMember, role: TeamRole) {
  await teamStore.updateMemberRole(teamId.value, member.user.id, { role });
}

async function handleRemove(member: TeamMember) {
  await teamStore.removeMember(teamId.value, member.user.id);
}

async function handleCancelInvitation(invitation: TeamInvitation) {
  await teamStore.cancelInvitation(invitation.id);
}

onMounted(() => {
  void refresh();
});
</script>

<style scoped>
.team-members-view {
  max-width: 1120px;
  margin: 0 auto;
}

.page-header {
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

.page-header h1 {
  margin: 0 0 8px;
  color: var(--color-text);
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: var(--color-text-muted);
}

.state-alert {
  margin-bottom: 16px;
}

@media (max-width: 767px) {
  .page-header {
    display: grid;
  }
}
</style>
