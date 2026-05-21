import { api } from "./instance";
import type { AiPlanResponse } from "../types/app";
import type { ScheduleGenerateResponse } from "../types/schedule";

export function planWithAi(prompt: string, startDate: string, endDate: string, apply = true) {
  return api.post<AiPlanResponse>("/ai/plan", {
    prompt,
    start_date: startDate,
    end_date: endDate,
    apply
  });
}

export function explainSchedule(startDate: string, endDate: string) {
  return api.post<ScheduleGenerateResponse>("/ai/explain", {
    start_date: startDate,
    end_date: endDate
  });
}

export function getSuggestions() {
  return api.get<{ suggestions: string[] }>("/ai/suggestions");
}
