<template>
  <a-form layout="vertical" class="work-log-form" @finish="handleSubmit">
    <a-form-item v-if="mode === 'log'" label="工作日期" required>
      <a-date-picker v-model:value="workDate" :disabled-date="disableFutureDate" />
    </a-form-item>
    <a-form-item v-if="mode === 'log'" label="工时" required>
      <a-input-number v-model:value="form.hours" :min="0.5" :max="24" :step="0.5" />
    </a-form-item>
    <a-form-item v-if="mode === 'log'" label="工作类型" required>
      <a-input v-model:value="form.work_type" />
    </a-form-item>
    <a-alert v-if="error" type="error" show-icon>
      <template #message>{{ error }}</template>
    </a-alert>
    <a-form-item v-if="mode === 'log'" label="工作内容" required>
      <a-textarea v-model:value="form.content" :rows="3" />
    </a-form-item>
    <a-checkbox v-if="mode === 'log'" v-model:checked="form.is_blocked">同时标记为阻塞</a-checkbox>
    <a-form-item v-if="form.is_blocked" label="阻塞原因" required extra="至少 10 个字符">
      <a-textarea v-model:value="form.blocked_reason" :rows="2" />
    </a-form-item>
    <a-form-item v-if="mode === 'log'" label="Commit Hash（可选）">
      <a-input v-model:value="form.commit_hash" />
    </a-form-item>
    <a-form-item v-if="mode === 'log'" label="分支名称（可选）">
      <a-input v-model:value="form.branch_name" />
    </a-form-item>
    <a-form-item v-if="mode === 'log'" label="仓库地址（可选）">
      <a-input v-model:value="form.repository_url" />
    </a-form-item>
    <a-button type="primary" html-type="submit" :loading="saving">{{ mode === "blocker" ? "确认标记阻塞" : "记录工作日志" }}</a-button>
  </a-form>
</template>

<script setup lang="ts">
import dayjs, { type Dayjs } from "dayjs";
import { ref, watch } from "vue";

import type { WorkLogCreatePayload } from "../../types/task";

const props = withDefaults(defineProps<{ saving: boolean; mode?: "log" | "blocker" }>(), { mode: "log" });
const emit = defineEmits<{ submit: [payload: WorkLogCreatePayload] }>();

const workDate = ref<Dayjs>(dayjs());
const error = ref("");
const form = ref({
  hours: 1,
  content: "",
  work_type: "GENERAL",
  is_blocked: false,
  blocked_reason: "",
  commit_hash: "",
  branch_name: "",
  repository_url: ""
});

watch(
  () => props.mode,
  (mode) => {
    form.value.is_blocked = mode === "blocker";
    error.value = "";
  },
  { immediate: true }
);

function disableFutureDate(current: Dayjs) {
  return current && current.isAfter(dayjs(), "day");
}

function handleSubmit() {
  error.value = "";
  const content = props.mode === "blocker" ? "标记任务阻塞" : form.value.content.trim();
  if (!content) {
    error.value = "请填写工作内容。";
    return;
  }
  if (form.value.is_blocked && form.value.blocked_reason.trim().length < 10) {
    error.value = "阻塞原因至少需要 10 个字符。";
    return;
  }
  emit("submit", {
    work_date: workDate.value.format("YYYY-MM-DD"),
    hours: form.value.hours,
    content,
    work_type: form.value.work_type,
    is_blocked: form.value.is_blocked,
    blocked_reason: form.value.is_blocked ? form.value.blocked_reason : null,
    commit_hash: form.value.commit_hash || null,
    branch_name: form.value.branch_name || null,
    repository_url: form.value.repository_url || null
  });
  form.value.content = "";
  form.value.blocked_reason = "";
  form.value.is_blocked = props.mode === "blocker";
}
</script>

<style scoped>
.work-log-form {
  display: grid;
  gap: 4px;
}
</style>
