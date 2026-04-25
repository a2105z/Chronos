import { api } from "./instance";
import type { ConstraintCreate } from "../types/constraint";

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
