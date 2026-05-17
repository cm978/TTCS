import { defineStore } from "pinia";

import { getCurrentUser, loginUser, registerUser } from "../api/auth";
import { authTokenKey, setUnauthorizedHandler } from "../api/client";
import type { LoginPayload, RegisterPayload, UserPublic } from "../types/auth";

interface AuthState {
  token: string | null;
  user: UserPublic | null;
  loading: boolean;
  hydrated: boolean;
  error: string | null;
}

function safeAuthError(fallback: string): string {
  return fallback;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    token: window.localStorage.getItem(authTokenKey),
    user: null,
    loading: false,
    hydrated: false,
    error: null
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user)
  },
  actions: {
    bindUnauthorizedHandler() {
      setUnauthorizedHandler(() => {
        this.logout();
      });
    },
    setToken(token: string) {
      this.token = token;
      window.localStorage.setItem(authTokenKey, token);
    },
    clearSession() {
      this.token = null;
      this.user = null;
      window.localStorage.removeItem(authTokenKey);
    },
    async register(payload: RegisterPayload) {
      this.loading = true;
      this.error = null;
      try {
        return await registerUser(payload);
      } catch {
        this.error = safeAuthError("创建账号失败。请检查表单信息后重试。");
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async login(payload: LoginPayload) {
      this.loading = true;
      this.error = null;
      try {
        const result = await loginUser(payload);
        this.setToken(result.access_token);
        this.user = result.user;
        this.hydrated = true;
        return result.user;
      } catch {
        this.error = safeAuthError("登录失败。请检查邮箱和密码后重试。");
        this.clearSession();
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
    async loadCurrentUser() {
      if (!this.token) {
        this.token = window.localStorage.getItem(authTokenKey);
      }
      if (!this.token) {
        this.hydrated = true;
        return null;
      }
      this.loading = true;
      this.error = null;
      try {
        this.user = await getCurrentUser();
        return this.user;
      } catch {
        this.error = safeAuthError("请求失败。请检查本地服务是否启动，然后重试。");
        this.clearSession();
        return null;
      } finally {
        this.hydrated = true;
        this.loading = false;
      }
    },
    logout() {
      this.clearSession();
      this.hydrated = true;
    }
  }
});
