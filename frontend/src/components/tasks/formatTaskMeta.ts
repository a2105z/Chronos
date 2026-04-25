import type { Task } from "../../types/task";

export function buildTaskMetaLine(task: Task): string {
  let parts: string[] = [];
  parts.push(`${task.estimated_duration_minutes} min`);
  parts.push(`Priority ${task.priority}`);

  if (task.splittable) {
    parts.push("Splittable");
  }

  if (task.deadline) {
    let deadlineLabel = new Date(task.deadline).toLocaleDateString();
    parts.push(`Deadline ${deadlineLabel}`);
  }

  let preferred = task.preferred_time_of_day;
  if (preferred && preferred !== "anytime") {
    parts.push(`Prefers ${preferred}`);
  }

  return parts.join(" · ");
}
