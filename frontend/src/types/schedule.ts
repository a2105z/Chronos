export interface ScheduledBlock {
  id: number;
  task_id: number;
  task_name: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
}

export interface UnscheduledDiagnostic {
  task_id: number;
  task_name: string;
  reason: string;
  detail: string;
}

export interface ScheduleGenerateResponse {
  blocks: ScheduledBlock[];
  unscheduled: UnscheduledDiagnostic[];
  summary: string;
}

export type AppView = "plan" | "calendar" | "tasks" | "availability" | "constraints";
