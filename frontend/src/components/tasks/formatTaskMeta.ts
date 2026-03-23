/** One readable line of metadata under a task name. */

import type { Task } from "../../types/task";

export function buildTaskMetaLine(task: Task): string {
  const parts: string[] = [];
  parts.push(`${task.estimated_duration_minutes} min`);
  parts.push(`Priority ${task.priority}`);

  if (task.splittable) {
    parts.push("Splittable");
  }

  if (task.deadline) {
    const deadlineLabel = new Date(task.deadline).toLocaleDateString();
    parts.push(`Deadline ${deadlineLabel}`);
  }

  const preferred = task.preferred_time_of_day;
  if (preferred && preferred !== "anytime") {
    parts.push(`Prefers ${preferred}`);
  }

  return parts.join(" · ");
}
