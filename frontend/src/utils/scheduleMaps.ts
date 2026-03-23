/** Group scheduled blocks and leftover tasks by calendar day. */

import type { Task } from "../types/task";
import type { ScheduledBlock } from "../types/schedule";
import { getDateKey } from "./calendarGrid";

export function buildBlocksByDay(blocks: ScheduledBlock[]): Map<string, ScheduledBlock[]> {
  const map = new Map<string, ScheduledBlock[]>();
  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    const key = getDateKey(new Date(block.start_time));
    const existing = map.get(key);
    if (existing) {
      existing.push(block);
    } else {
      map.set(key, [block]);
    }
  }
  return map;
}

export function buildScheduledTaskIds(blocks: ScheduledBlock[]): Set<number> {
  const ids = new Set<number>();
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
  const map = new Map<string, Task[]>();
  for (let i = 0; i < tasks.length; i++) {
    const task = tasks[i];
    if (scheduledTaskIds.has(task.id)) {
      continue;
    }
    let targetDate = new Date(weekStart);
    if (task.deadline) {
      targetDate = new Date(task.deadline);
    }
    const key = getDateKey(targetDate);
    const existing = map.get(key);
    if (existing) {
      existing.push(task);
    } else {
      map.set(key, [task]);
    }
  }
  return map;
}

export function getListForDay<T>(map: Map<string, T[]>, dayKey: string): T[] {
  const found = map.get(dayKey);
  if (found) {
    return found;
  }
  return [];
}
