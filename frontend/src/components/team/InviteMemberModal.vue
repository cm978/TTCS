<template>
  <a-modal :open="open" title="邀请成员" :footer="null" @update:open="emit('update:open', $event)">
    <a-alert v-if="error" type="error" show-icon class="form-alert">
      <template #message>{{ error }}</template>
    </a-alert>
    <a-form :model="form" :rules="rules" layout="vertical" @finish="handleSubmit">
      <a-form-item label="邮箱" name="email" extra="未注册邮箱也可以先创建待接受邀请。">
        <a-input v-model:value="form.email" type="email" autocomplete="email" />
      </a-form-item>
      <a-form-item label="团队角色" name="role">
        <a-select v-model:value="form.role">
          <a-select-option value="TEAM_ADMIN">管理员</a-select-option>
          <a-select-option value="TEAM_MEMBER">成员</a-select-option>
        </a-select>
      </a-form-item>
      <div class="modal-actions">
        <a-button :disabled="loading" @click="emit('update:open', false)">取消</a-button>
        <a-button type="primary" html-type="submit" :loading="loading" :disabled="!form.email.trim()">
          邀请成员
        </a-button>
      </div>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

import type { TeamInvitationCreatePayload, TeamRole } from "../../types/team";

const props = defineProps<{
  open: boolean;
  loading?: boolean;
  error?: string | null;
}>();

const emit = defineEmits<{
  "update:open": [value: boolean];
  submit: [payload: TeamInvitationCreatePayload];
}>();

const form = reactive<{ email: string; role: TeamRole }>({ email: "", role: "TEAM_MEMBER" });
const rules = {
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入有效邮箱", trigger: "blur" }
  ],
  role: [{ required: true, message: "请选择团队角色", trigger: "change" }]
};

function handleSubmit() {
  emit("submit", { email: form.email.trim(), role: form.role });
}

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      form.email = "";
      form.role = "TEAM_MEMBER";
    }
  }
);
</script>

<style scoped>
.form-alert {
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
