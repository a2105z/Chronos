/** Default values for the "create task" form. */

import type { TaskCreate } from "../../types/task";

export const DEFAULT_TASK_FORM: TaskCreate = {
  name: "",
  estimated_duration_minutes: 30,
  priority: 0,
  deadline: null,
  preferred_time_of_day: "anytime",
  splittable: false,
};
