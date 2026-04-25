import { api } from "./instance";

export function getSchedule(startDate: string, endDate: string) {
  return api.get("/schedule", { params: { start_date: startDate, end_date: endDate } });
}

export function generateSchedule(startDate: string, endDate: string) {
  return api.post("/schedule", {
    start_date: startDate,
    end_date: endDate,
    replace_existing: true
  });
}

export function moveScheduleBlock(blockId: number, startTimeIso: string) {
  return api.patch(`/schedule/blocks/${blockId}`, { start_time: startTimeIso });
}

export function deleteScheduleBlock(blockId: number) {
  return api.delete(`/schedule/blocks/${blockId}`);
}

export function exportSchedule(startDate: string, endDate: string) {
  return api.post(
    "/schedule/export",
    { start_date: startDate, end_date: endDate },
    { responseType: "blob" }
  );
}
