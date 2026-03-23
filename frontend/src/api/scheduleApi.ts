/** Schedule generation and export. */

import { api } from "./instance";

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
