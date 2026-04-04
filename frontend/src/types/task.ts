export type PreferredTimeOfDay = "anytime" | "morning" | "afternoon" | "evening";

export interface Task {
  id: number;
  name: string;
  estimated_duration_minutes: number;
  priority: number;
  earliest_start?: string | null;
  deadline?: string | null;
  preferred_time_of_day?: PreferredTimeOfDay;
  splittable: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  name: string;
  estimated_duration_minutes: number;
  priority?: number;
  earliest_start?: string | null;
  deadline?: string | null;
  preferred_time_of_day?: PreferredTimeOfDay;
  splittable?: boolean;
}

/** Partial update payload for PUT /api/tasks/:id */
export type TaskUpdate = Partial<TaskCreate>;
