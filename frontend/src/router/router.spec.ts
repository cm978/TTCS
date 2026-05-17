import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getCurrentUser } from "../api/auth";
import { authTokenKey } from "../api/client";
import router from "./index";

vi.mock("../api/auth", () => ({
  getCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  registerUser: vi.fn()
}));

describe("router guards", () => {
  beforeEach(async () => {
    setActivePinia(createPinia());
    await router.push("/login");
    vi.clearAllMocks();
  });

  it("redirects anonymous users away from protected route", async () => {
    await router.push("/app");

    expect(router.currentRoute.value.name).toBe("login");
  });

  it("allows protected route when stored token loads current user", async () => {
    window.localStorage.setItem(authTokenKey, "jwt-token");
    vi.mocked(getCurrentUser).mockResolvedValue({
      id: 1,
      email: "moon@example.com",
      display_name: "Moon",
      is_active: true,
      created_at: "2026-05-17T00:00:00Z"
    });

    await router.push("/app");

    expect(router.currentRoute.value.name).toBe("foundation");
  });
});

