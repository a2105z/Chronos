import { api } from "./instance";
import type { ScheduleGenerateResponse, ScheduledBlock } from "../types/schedule";

export function getSchedule(startDate: string, endDate: string) {
  return api.get<ScheduledBlock[]>("/schedule", {
    params: { start_date: startDate, end_date: endDate }
  });
}

export function generateSchedule(startDate: string, endDate: string, replaceExisting = true) {
  return api.post<ScheduleGenerateResponse>("/schedule", {
    start_date: startDate,
    end_date: endDate,
    replace_existing: replaceExisting
  });
}

export function moveScheduleBlock(
  blockId: number,
  startTimeIso: string,
  endTimeIso?: string
) {
  const body: { start_time: string; end_time?: string } = { start_time: startTimeIso };
  if (endTimeIso) {
    body.end_time = endTimeIso;
  }
  return api.patch<ScheduledBlock>(`/schedule/blocks/${blockId}`, body);
}

export function createScheduleBlock(title: string, startTimeIso: string, endTimeIso: string) {
  return api.post<ScheduledBlock>("/schedule/blocks", {
    title,
    start_time: startTimeIso,
    end_time: endTimeIso
  });
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
