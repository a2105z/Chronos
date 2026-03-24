/** API client - axios instance and endpoint helpers. */

import axios from "axios";
import type { TaskCreate } from "../types/task";
import type { AvailabilityCreate } from "../types/availability";
import type { ConstraintCreate } from "../types/constraint";


const API_BASE = "/api";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});


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


export function getAvailability() {
  return api.get("/availability");
}

export function createAvailability(data: AvailabilityCreate) {
  return api.post("/availability", data);
}

export function updateAvailability(id: number, data: Partial<AvailabilityCreate>) {
  return api.put(`/availability/${id}`, data);
}

export function deleteAvailability(id: number) {
  return api.delete(`/availability/${id}`);
}


export function getConstraints() {
  return api.get("/constraints");
}

export function createConstraint(data: ConstraintCreate) {
  return api.post("/constraints", data);
}

export function updateConstraint(id: number, data: Partial<ConstraintCreate>) {
  return api.put(`/constraints/${id}`, data);
}

export function deleteConstraint(id: number) {
  return api.delete(`/constraints/${id}`);
}


export function generateSchedule(startDate: string, endDate: string) {
  return api.post("/schedule", {
    start_date: startDate,
    end_date: endDate,
    replace_existing: true,
  });
}

export function exportSchedule(startDate: string, endDate: string) {
  return api.post(
    "/schedule/export",
    { start_date: startDate, end_date: endDate },
    { responseType: "blob" }
  );
}
