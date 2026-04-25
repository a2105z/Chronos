import { api } from "./instance";
import type { TaskCreate, TaskUpdate } from "../types/task";

export function getTasks() {
  return api.get("/tasks");
}

export function createTask(data: TaskCreate) {
  return api.post("/tasks", data);
}

export function updateTask(id: number, data: TaskUpdate) {
  return api.put(`/tasks/${id}`, data);
}

export function deleteTask(id: number) {
  return api.delete(`/tasks/${id}`);
}
