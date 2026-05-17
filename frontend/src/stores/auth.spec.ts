import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getCurrentUser, loginUser, registerUser } from "../api/auth";
import { authTokenKey } from "../api/client";
import { useAuthStore } from "./auth";

vi.mock("../api/auth", () => ({
  getCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  registerUser: vi.fn()
}));

const user = {
  id: 1,
  email: "moon@example.com",
  display_name: "Moon",
  is_active: true,
  created_at: "2026-05-17T00:00:00Z"
};

describe("auth store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("persists token after login", async () => {
    vi.mocked(loginUser).mockResolvedValue({ access_token: "jwt-token", token_type: "bearer", expires_in: 86400, user });
    const auth = useAuthStore();

    await auth.login({ email: "moon@example.com", password: "SecurePass123!" });

    expect(window.localStorage.getItem(authTokenKey)).toBe("jwt-token");
    expect(auth.user?.email).toBe("moon@example.com");
  });

  it("recovers current user from stored token", async () => {
    window.localStorage.setItem(authTokenKey, "jwt-token");
    vi.mocked(getCurrentUser).mockResolvedValue(user);
    const auth = useAuthStore();

    await auth.loadCurrentUser();

    expect(auth.user?.id).toBe(1);
    expect(auth.isAuthenticated).toBe(true);
  });

  it("clears token on logout", () => {
    const auth = useAuthStore();
    auth.setToken("jwt-token");

    auth.logout();

    expect(window.localStorage.getItem(authTokenKey)).toBeNull();
    expect(auth.user).toBeNull();
  });

  it("registers with the API without storing profile data", async () => {
    vi.mocked(registerUser).mockResolvedValue(user);
    const auth = useAuthStore();

    await auth.register({ email: "moon@example.com", password: "SecurePass123!" });

    expect(registerUser).toHaveBeenCalledWith({ email: "moon@example.com", password: "SecurePass123!" });
    expect(window.localStorage.getItem(authTokenKey)).toBeNull();
  });
});

