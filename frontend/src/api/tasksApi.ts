/** Task CRUD endpoints. */

import { api } from "./instance";
import type { TaskCreate } from "../types/task";

export function getTasks() {
  return api.get("/tasks");
}

export function createTask(data: TaskCreate) {
  return api.post("/tasks", data);
}

export function updateTask(id: number, data: Partial<TaskCreate>) {
  return api.put(`/tasks/${id}`, data);
}

export function deleteTask(id: number) {
  return api.delete(`/tasks/${id}`);
}
