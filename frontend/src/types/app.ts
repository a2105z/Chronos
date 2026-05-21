export type AppView = "plan" | "calendar" | "tasks" | "availability" | "constraints";

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface PlanIntent {
  raw_prompt: string;
  tasks: Array<{
    name: string;
    estimated_duration_minutes: number;
    priority: number;
    preferred_time_of_day?: string | null;
    deadline?: string | null;
    earliest_start?: string | null;
    splittable: boolean;
  }>;
  availability: Array<{
    day_of_week: number;
    start_minutes: number;
    end_minutes: number;
    weekdays_only: boolean;
  }>;
  constraints: Array<{
    constraint_type: string;
    day_of_week?: number | null;
    start_minutes?: number | null;
    end_minutes?: number | null;
    value?: number | null;
    every_weekday: boolean;
  }>;
  notes: string[];
  parser: string;
}

export interface AiPlanResponse {
  intent: PlanIntent;
  created: {
    tasks: Array<{ id?: number; name?: string; [key: string]: unknown }>;
    availability: Array<Record<string, unknown>>;
    constraints: Array<Record<string, unknown>>;
  };
  schedule: {
    blocks: import("./schedule").ScheduledBlock[];
    unscheduled: import("./schedule").UnscheduledDiagnostic[];
    summary: string;
  } | null;
  assistant_message: string;
}
