<template>
  <AuthFrame mode="login">
    <a-form layout="vertical" :model="form" @finish="handleSubmit">
      <a-alert v-if="auth.error" class="auth-error" type="error" show-icon :message="auth.error" />

      <a-form-item label="邮箱" name="email" :rules="[{ required: true, type: 'email', message: '请输入有效邮箱' }]">
        <a-input v-model:value="form.email" autocomplete="email" size="large" />
      </a-form-item>

      <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]">
        <a-input-password v-model:value="form.password" autocomplete="current-password" size="large" />
      </a-form-item>

      <a-button class="auth-submit" type="primary" html-type="submit" size="large" :loading="auth.loading" :disabled="auth.loading">
        登录 TTCS
      </a-button>

      <p class="auth-switch">
        还没有账号？
        <RouterLink to="/register">创建账号</RouterLink>
      </p>
    </a-form>
  </AuthFrame>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthFrame from "../views/parts/AuthFrame.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const form = reactive({ email: "", password: "" });

async function handleSubmit() {
  await auth.login(form);
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/app";
  router.push(redirect);
}
</script>

<style scoped>
.auth-error {
  margin-bottom: 16px;
}

.auth-submit {
  width: 100%;
  min-height: 44px;
}

.auth-switch {
  margin: 18px 0 0;
  color: var(--color-text-muted);
  text-align: center;
}
</style>

