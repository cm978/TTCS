<template>
  <main class="auth-page">
    <section class="auth-panel" aria-labelledby="auth-title">
      <div class="auth-brand">
        <ShieldCheck :size="28" aria-hidden="true" />
        <span>TTCS</span>
      </div>
      <h1 id="auth-title">{{ title }}</h1>
      <p>{{ subtitle }}</p>
      <slot />
    </section>

    <aside class="signal-panel" aria-label="TTCS 工作闭环">
      <div class="signal-step">
        <FileCheck2 :size="20" aria-hidden="true" />
        <span>证据记录</span>
      </div>
      <div class="signal-step signal-step--review">
        <MessagesSquare :size="20" aria-hidden="true" />
        <span>人工验收</span>
      </div>
      <div class="signal-step signal-step--success">
        <CheckCircle2 :size="20" aria-hidden="true" />
        <span>确认完成</span>
      </div>
    </aside>
  </main>
</template>

<script setup lang="ts">
import { CheckCircle2, FileCheck2, MessagesSquare, ShieldCheck } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps<{ mode: "login" | "register" }>();

const title = computed(() => (props.mode === "login" ? "登录 TTCS" : "创建账号"));
const subtitle = computed(() =>
  props.mode === "login" ? "进入受保护的任务协作基础壳。" : "创建本地演示账号，开始验证认证闭环。"
);
</script>

<style scoped>
.auth-page {
  min-height: 100dvh;
  display: grid;
  grid-template-columns: minmax(320px, 440px) minmax(0, 1fr);
  gap: 48px;
  align-items: center;
  padding: 32px;
  background:
    linear-gradient(135deg, rgba(37, 99, 235, 0.10), transparent 42%),
    var(--color-bg);
}

.auth-panel {
  width: 100%;
  padding: 32px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-primary);
  font-size: 20px;
  font-weight: 700;
}

h1 {
  margin: 24px 0 8px;
  font-size: 32px;
  line-height: 1.15;
}

p {
  margin: 0 0 24px;
  color: var(--color-text-muted);
  line-height: 1.6;
}

.signal-panel {
  display: grid;
  gap: 16px;
  max-width: 520px;
}

.signal-step {
  min-height: 88px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-primary);
  font-weight: 650;
}

.signal-step--review {
  color: var(--color-review);
}

.signal-step--success {
  color: var(--color-success);
}

@media (max-width: 767px) {
  .auth-page {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .auth-panel {
    padding: 24px;
  }

  .signal-panel {
    display: none;
  }
}
</style>

