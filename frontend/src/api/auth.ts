import { apiClient } from "./client";
import type { LoginPayload, RegisterPayload, TokenResponse, UserPublic } from "../types/auth";

export async function registerUser(payload: RegisterPayload): Promise<UserPublic> {
  const { data } = await apiClient.post<UserPublic>("/auth/register", payload);
  return data;
}

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
  return data;
}

export async function getCurrentUser(): Promise<UserPublic> {
  const { data } = await apiClient.get<UserPublic>("/auth/me");
  return data;
}

