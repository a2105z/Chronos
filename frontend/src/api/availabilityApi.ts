/** Availability window endpoints. */

import { api } from "./instance";
import type { AvailabilityCreate } from "../types/availability";

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
