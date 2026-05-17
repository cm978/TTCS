<template>
  <AppLayout>
    <section class="route-placeholder">
      <h1>项目看板</h1>
      <p>基础看板将展示项目的真实列和成员。</p>
    </section>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from "../layouts/AppLayout.vue";
</script>

<style scoped>
.route-placeholder {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.route-placeholder h1 {
  margin: 0 0 8px;
  color: var(--color-text);
  font-size: 24px;
}

.route-placeholder p {
  margin: 0;
  color: var(--color-text-muted);
}
</style>
