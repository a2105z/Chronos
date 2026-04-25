import type { Task } from "../types/task";
import type { ScheduledBlock } from "../types/schedule";
import { getDateKey } from "./calendarGrid";

export function buildBlocksByDay(blocks: ScheduledBlock[]): Map<string, ScheduledBlock[]> {
  let map = new Map<string, ScheduledBlock[]>();
  for (let i = 0; i < blocks.length; i++) {
    let block = blocks[i];
    let key = getDateKey(new Date(block.start_time));
    let existing = map.get(key);
    if (existing) {
      existing.push(block);
    } else {
      map.set(key, [block]);
    }
  }
  return map;
}

export function buildScheduledTaskIds(blocks: ScheduledBlock[]): Set<number> {
  let ids = new Set<number>();
  for (let i = 0; i < blocks.length; i++) {
    ids.add(blocks[i].task_id);
  }
  return ids;
}

export function buildUnscheduledTasksByDay(
  tasks: Task[],
  weekStart: Date,
  scheduledTaskIds: Set<number>
): Map<string, Task[]> {
  let map = new Map<string, Task[]>();
  for (let i = 0; i < tasks.length; i++) {
    let task = tasks[i];
    if (scheduledTaskIds.has(task.id)) {
      continue;
    }
    let targetDate = new Date(weekStart);
    if (task.deadline) {
      targetDate = new Date(task.deadline);
    }
    let key = getDateKey(targetDate);
    let existing = map.get(key);
    if (existing) {
      existing.push(task);
    } else {
      map.set(key, [task]);
    }
  }
  return map;
}

export function getListForDay<T>(map: Map<string, T[]>, dayKey: string): T[] {
  let found = map.get(dayKey);
  if (found) {
    return found;
  }
  return [];
}
