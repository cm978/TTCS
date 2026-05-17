<template>
  <a-modal :open="open" title="创建团队" :footer="null" @update:open="emit('update:open', $event)">
    <a-alert v-if="error" type="error" show-icon class="form-alert">
      <template #message>{{ error }}</template>
    </a-alert>
    <a-form layout="vertical" @finish="handleSubmit">
      <a-form-item label="团队名称" name="name" extra="2-50 个字符，团队名称需唯一" required>
        <a-input v-model:value="form.name" :maxlength="50" autocomplete="off" />
      </a-form-item>
      <a-form-item label="团队描述" name="description" extra="最多 500 个字符">
        <a-textarea v-model:value="form.description" :maxlength="500" :rows="3" />
      </a-form-item>
      <p v-if="created" class="success-copy" aria-live="polite">团队已创建，你已成为团队管理员。</p>
      <div class="modal-actions">
        <a-button :disabled="loading" @click="emit('update:open', false)">取消</a-button>
        <a-button type="primary" html-type="submit" :loading="loading" :disabled="form.name.trim().length < 2">
          创建团队
        </a-button>
      </div>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

import type { TeamCreatePayload } from "../../types/team";

const props = defineProps<{
  open: boolean;
  loading?: boolean;
  error?: string | null;
  created?: boolean;
}>();

const emit = defineEmits<{
  "update:open": [value: boolean];
  submit: [payload: TeamCreatePayload];
}>();

const form = reactive({ name: "", description: "" });

function handleSubmit() {
  emit("submit", { name: form.name.trim(), description: form.description.trim() || null });
}

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      form.name = "";
      form.description = "";
    }
  }
);
</script>

<style scoped>
.form-alert {
  margin-bottom: 16px;
}

.success-copy {
  margin: 0 0 16px;
  color: var(--color-success);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
