import { api } from "./instance";
import type { User } from "../types/app";

export function register(email: string, password: string, name: string) {
  return api.post<User>("/auth/register", { email, password, name });
}

export function login(email: string, password: string) {
  return api.post<{ access_token: string; token_type: string }>("/auth/login", {
    email,
    password
  });
}

export function getMe() {
  return api.get<User>("/auth/me");
}
