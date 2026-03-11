export interface Constraint {
  id: number;
  constraint_type: string;
  day_of_week?: number | null;
  start_minutes?: number | null;
  end_minutes?: number | null;
  value?: number | null;
  metadata_json?: string | null;
}

export interface ConstraintCreate {
  constraint_type: string;
  day_of_week?: number;
  start_minutes?: number;
  end_minutes?: number;
  value?: number;
}
