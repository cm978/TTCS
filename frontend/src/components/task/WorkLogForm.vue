<template>
  <div class="work-log-form">
    <div v-if="mode === 'log'" class="form-grid">
      <label class="field">
        <span>工作日期 <b>*</b></span>
        <input v-model="form.work_date" class="native-input" type="date" />
      </label>
      <label class="field">
        <span>工时 <b>*</b></span>
        <input v-model.number="form.hours" class="native-input" type="number" min="0.5" max="24" step="0.5" />
      </label>
    </div>
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
    <section v-if="mode === 'log'" class="code-evidence">
      <h4>代码证据（可选）</h4>
      <p>仅手动记录，不会连接 Git 平台或自动校验提交。</p>
      <a-form-item label="Commit Hash">
        <a-input v-model:value="form.commit_hash" />
      </a-form-item>
      <a-form-item label="分支名称">
        <a-input v-model:value="form.branch_name" />
      </a-form-item>
      <a-form-item label="仓库地址">
        <a-input v-model:value="form.repository_url" />
      </a-form-item>
    </section>
    <a-button type="primary" :loading="saving" @click="handleSubmit">{{ mode === "blocker" ? "确认标记阻塞" : "记录工作日志" }}</a-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

import type { WorkLogCreatePayload } from "../../types/task";

const props = withDefaults(defineProps<{ saving: boolean; mode?: "log" | "blocker" }>(), { mode: "log" });
const emit = defineEmits<{ submit: [payload: WorkLogCreatePayload] }>();

const error = ref("");
const form = ref({
  work_date: new Date().toISOString().slice(0, 10),
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

function handleSubmit() {
  error.value = "";
  if (props.mode === "log" && !form.value.work_date) {
    error.value = "请填写工作日期。";
    return;
  }
  if (props.mode === "log" && (form.value.hours < 0.5 || form.value.hours > 24 || (form.value.hours * 2) % 1 !== 0)) {
    error.value = "工时必须在 0.5 到 24 小时之间，并以 0.5 小时递增。";
    return;
  }
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
    work_date: form.value.work_date,
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
  gap: 12px;
}

.form-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.form-grid > * {
  flex: 1 1 180px;
}

.field {
  display: grid;
  gap: 8px;
  color: var(--color-text);
  font-weight: 600;
}

.field b {
  color: var(--color-danger);
}

.native-input {
  min-height: 40px;
  padding: 6px 11px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
}

.native-input:focus {
  border-color: var(--color-primary);
  outline: 2px solid color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.code-evidence {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-raised);
}

.code-evidence h4,
.code-evidence p {
  margin: 0;
}

.code-evidence p {
  color: var(--color-text-muted);
  font-size: 14px;
}
</style>
