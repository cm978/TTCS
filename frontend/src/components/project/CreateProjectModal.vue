<template>
  <a-modal :open="open" title="创建项目" :footer="null" @update:open="emit('update:open', $event)">
    <a-alert v-if="formError || error" type="error" show-icon class="form-alert">
      <template #message>{{ formError || error }}</template>
    </a-alert>
    <a-form :model="form" :rules="rules" layout="vertical" @finish="handleSubmit">
      <a-form-item label="项目名称" name="name" extra="2-100 个字符">
        <a-input v-model:value="form.name" :maxlength="100" autocomplete="off" />
      </a-form-item>
      <a-form-item label="项目描述" name="description" extra="最多 1000 个字符">
        <a-textarea v-model:value="form.description" :maxlength="1000" :rows="3" />
      </a-form-item>
      <div class="date-grid">
        <a-form-item label="开始日期" name="start_date">
          <a-input v-model:value="form.start_date" type="date" />
        </a-form-item>
        <a-form-item label="结束日期" name="end_date">
          <a-input v-model:value="form.end_date" type="date" />
        </a-form-item>
      </div>
      <p v-if="created" class="success-copy" aria-live="polite">项目已创建，默认看板已就绪。</p>
      <div class="modal-actions">
        <a-button :disabled="loading" @click="emit('update:open', false)">取消</a-button>
        <a-button type="primary" html-type="submit" :loading="loading" :disabled="form.name.trim().length < 2">
          创建项目
        </a-button>
      </div>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue";

import type { ProjectCreatePayload } from "../../types/project";

const props = defineProps<{
  open: boolean;
  loading?: boolean;
  error?: string | null;
  created?: boolean;
}>();

const emit = defineEmits<{
  "update:open": [value: boolean];
  submit: [payload: ProjectCreatePayload];
}>();

const form = reactive({ name: "", description: "", start_date: "", end_date: "" });
const formError = ref<string | null>(null);
const rules = {
  name: [
    { required: true, message: "请输入项目名称", trigger: "blur" },
    { min: 2, max: 100, message: "项目名称需为 2-100 个字符", trigger: "blur" }
  ],
  description: [{ max: 1000, message: "项目描述最多 1000 个字符", trigger: "blur" }]
};

function handleSubmit() {
  formError.value = null;
  if (form.start_date && form.end_date && form.end_date <= form.start_date) {
    formError.value = "结束日期必须晚于开始日期。";
    return;
  }
  emit("submit", {
    name: form.name.trim(),
    description: form.description.trim() || null,
    start_date: form.start_date || null,
    end_date: form.end_date || null
  });
}

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      form.name = "";
      form.description = "";
      form.start_date = "";
      form.end_date = "";
      formError.value = null;
    }
  }
);
</script>

<style scoped>
.form-alert {
  margin-bottom: 16px;
}

.date-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
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

@media (max-width: 560px) {
  .date-grid {
    grid-template-columns: 1fr;
  }
}
</style>
