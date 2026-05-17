<template>
  <AppLayout>
    <section class="foundation">
      <div class="foundation__intro">
        <a-tag color="blue">Phase 1</a-tag>
        <h1>基础认证已就绪</h1>
        <p>你已进入受保护的 TTCS 应用壳。团队、项目和任务能力将在后续阶段接入。</p>
      </div>

      <div class="status-grid">
        <article class="status-card">
          <KeyRound :size="22" aria-hidden="true" />
          <div>
            <h2>认证会话</h2>
            <p>JWT Bearer 会话已建立，刷新浏览器后会通过 /me 恢复。</p>
          </div>
        </article>
        <article class="status-card">
          <UserRoundCheck :size="22" aria-hidden="true" />
          <div>
            <h2>当前用户</h2>
            <p>{{ auth.user?.display_name || auth.user?.email }}</p>
          </div>
        </article>
        <article class="status-card status-card--review">
          <Route :size="22" aria-hidden="true" />
          <div>
            <h2>后续切片</h2>
            <p>此壳体会承载团队、项目、任务和验收闭环，但当前不展示虚假数据。</p>
          </div>
        </article>
      </div>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import { KeyRound, Route, UserRoundCheck } from "lucide-vue-next";

import AppLayout from "../layouts/AppLayout.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
</script>

<style scoped>
.foundation {
  max-width: 1120px;
  margin: 0 auto;
}

.foundation__intro {
  padding: 28px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.foundation__intro h1 {
  margin: 16px 0 10px;
  font-size: 32px;
  line-height: 1.15;
}

.foundation__intro p {
  max-width: 680px;
  margin: 0;
  color: var(--color-text-muted);
  font-size: 16px;
  line-height: 1.6;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.status-card {
  display: flex;
  gap: 14px;
  padding: 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.status-card svg {
  flex: 0 0 auto;
  color: var(--color-primary);
}

.status-card--review svg {
  color: var(--color-review);
}

.status-card h2 {
  margin: 0 0 8px;
  font-size: 16px;
}

.status-card p {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.55;
}

@media (max-width: 900px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>

