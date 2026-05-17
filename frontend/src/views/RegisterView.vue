<template>
  <AuthFrame mode="register">
    <a-form layout="vertical" :model="form" @finish="handleSubmit">
      <a-alert v-if="auth.error" class="auth-error" type="error" show-icon :message="auth.error" />

      <a-form-item label="显示名称" name="display_name">
        <a-input v-model:value="form.display_name" autocomplete="name" size="large" />
      </a-form-item>

      <a-form-item label="邮箱" name="email" :rules="[{ required: true, type: 'email', message: '请输入有效邮箱' }]">
        <a-input v-model:value="form.email" autocomplete="email" size="large" />
      </a-form-item>

      <a-form-item label="密码" name="password" :rules="[{ required: true, min: 8, message: '密码至少 8 个字符' }]">
        <a-input-password v-model:value="form.password" autocomplete="new-password" size="large" />
      </a-form-item>

      <a-button class="auth-submit" type="primary" html-type="submit" size="large" :loading="auth.loading" :disabled="auth.loading">
        创建账号
      </a-button>

      <p class="auth-switch">
        已有账号？
        <RouterLink to="/login">登录 TTCS</RouterLink>
      </p>
    </a-form>
  </AuthFrame>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { useRouter } from "vue-router";

import AuthFrame from "../views/parts/AuthFrame.vue";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const form = reactive({ display_name: "", email: "", password: "" });

async function handleSubmit() {
  await auth.register(form);
  await auth.login({ email: form.email, password: form.password });
  router.push("/app");
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

