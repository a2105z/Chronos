export interface Availability {
  id: number;
  day_of_week: number;
  start_minutes: number;
  end_minutes: number;
}

export interface AvailabilityCreate {
  day_of_week: number;
  start_minutes: number;
  end_minutes: number;
}
