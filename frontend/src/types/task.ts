export interface Task {
  id: number;
  name: string;
  estimated_duration_minutes: number;
  priority: number;
  deadline: string | null;
  splittable: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  name: string;
  estimated_duration_minutes: number;
  priority?: number;
  deadline?: string | null;
  splittable?: boolean;
}
