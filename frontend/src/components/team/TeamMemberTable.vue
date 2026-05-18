<template>
  <div class="member-table" aria-label="团队成员表">
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>成员/邮箱</th>
            <th>显示名</th>
            <th>团队角色</th>
            <th>状态</th>
            <th>加入/邀请时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="`member-${member.id}`">
            <td>{{ member.user.email }}</td>
            <td>{{ member.user.display_name || "未设置" }}</td>
            <td>
              <a-select
                :value="member.role"
                :disabled="!isAdmin || isLastAdmin(member)"
                class="role-select"
                @change="(role: unknown) => emit('role-change', member, role as TeamRole)"
              >
                <a-select-option value="TEAM_ADMIN">管理员</a-select-option>
                <a-select-option value="TEAM_MEMBER">成员</a-select-option>
              </a-select>
              <p v-if="isLastAdmin(member)" class="guard-copy">团队至少需要保留 1 名管理员。</p>
            </td>
            <td><a-tag color="green">已加入</a-tag></td>
            <td>{{ formatDate(member.created_at) }}</td>
            <td>
              <a-popconfirm
                title="移除成员：移除后该成员将无法继续访问对应团队或项目。"
                ok-text="移除"
                cancel-text="取消"
                :disabled="!isAdmin || isLastAdmin(member)"
                @confirm="emit('remove', member)"
              >
                <a-button danger size="small" :disabled="!isAdmin || isLastAdmin(member)">移除成员</a-button>
              </a-popconfirm>
            </td>
          </tr>
          <tr v-for="invitation in visibleInvitations" :key="`invitation-${invitation.id}`">
            <td>{{ invitation.email }}</td>
            <td>待注册或待接受</td>
            <td>{{ roleLabel(invitation.role) }}</td>
            <td><a-tag :color="invitationStatusColor(invitation.status)">{{ invitationStatusLabel(invitation.status) }}</a-tag></td>
            <td>{{ formatDate(invitation.created_at) }}</td>
            <td>
              <a-button
                danger
                size="small"
                :disabled="!isAdmin || invitation.status !== 'PENDING'"
                @click="emit('cancel-invitation', invitation)"
              >
                取消邀请
              </a-button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { TeamInvitation, TeamInvitationStatus, TeamMember, TeamRole } from "../../types/team";

const props = defineProps<{
  members: TeamMember[];
  invitations: TeamInvitation[];
  isAdmin: boolean;
}>();

const emit = defineEmits<{
  "role-change": [member: TeamMember, role: TeamRole];
  remove: [member: TeamMember];
  "cancel-invitation": [invitation: TeamInvitation];
}>();

const visibleInvitations = computed(() => props.invitations.filter((invitation) => invitation.status !== "ACCEPTED"));

function roleLabel(role: TeamRole) {
  return role === "TEAM_ADMIN" ? "管理员" : "成员";
}

function invitationStatusLabel(status: TeamInvitationStatus) {
  const labels: Record<TeamInvitationStatus, string> = {
    PENDING: "待接受邀请",
    ACCEPTED: "已接受",
    EXPIRED: "邀请已过期",
    CANCELLED: "邀请已取消"
  };
  return labels[status];
}

function invitationStatusColor(status: TeamInvitationStatus) {
  const colors: Record<TeamInvitationStatus, string> = {
    PENDING: "blue",
    ACCEPTED: "green",
    EXPIRED: "orange",
    CANCELLED: "red"
  };
  return colors[status];
}

function adminCount() {
  return props.members.filter((member) => member.role === "TEAM_ADMIN").length;
}

function isLastAdmin(member: TeamMember) {
  return member.role === "TEAM_ADMIN" && adminCount() <= 1;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" }).format(
    new Date(value)
  );
}
</script>

<style scoped>
.member-table {
  width: 100%;
}

.table-scroll {
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

table {
  width: 100%;
  min-width: 860px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
  vertical-align: top;
  color: var(--color-text);
  font-size: 14px;
}

th {
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 650;
}

tr:last-child td {
  border-bottom: 0;
}

.role-select {
  min-width: 132px;
}

.guard-copy {
  margin: 6px 0 0;
  color: var(--color-warning);
  font-size: 13px;
}
</style>
