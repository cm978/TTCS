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
  </main>
</template>

<script setup lang="ts">
import { ShieldCheck } from "lucide-vue-next";
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
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: var(--color-bg);
}

.auth-panel {
  width: 100%;
  max-width: 440px;
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

@media (max-width: 767px) {
  .auth-page {
    padding: 16px;
  }

  .auth-panel {
    padding: 24px;
  }
}
</style>
