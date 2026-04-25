import { describe, expect, it } from "vitest";
import { buildBlocksByDay, buildScheduledTaskIds, buildUnscheduledTasksByDay, getListForDay } from "../src/utils/scheduleMaps";
import type { ScheduledBlock } from "../src/types/schedule";
import type { Task } from "../src/types/task";

function mkTask(id: number, name: string, deadline?: string): Task {
  return {
    id,
    name,
    estimated_duration_minutes: 60,
    priority: 1,
    earliest_start: null,
    deadline: deadline ?? null,
    preferred_time_of_day: "anytime",
    splittable: false,
    created_at: "2030-01-01T00:00:00",
    updated_at: "2030-01-01T00:00:00"
  };
}

describe("scheduleMaps", () => {
  it("groups scheduled blocks by calendar day", () => {
    const blocks: ScheduledBlock[] = [
      {
        id: 1,
        task_id: 1,
        task_name: "Task A",
        start_time: "2030-01-07T09:00:00",
        end_time: "2030-01-07T10:00:00",
        duration_minutes: 60
      },
      {
        id: 2,
        task_id: 2,
        task_name: "Task B",
        start_time: "2030-01-08T11:00:00",
        end_time: "2030-01-08T12:00:00",
        duration_minutes: 60
      }
    ];

    const grouped = buildBlocksByDay(blocks);
    expect(getListForDay(grouped, "2030-01-07")).toHaveLength(1);
    expect(getListForDay(grouped, "2030-01-08")).toHaveLength(1);
  });

  it("keeps only unscheduled tasks and maps deadline tasks to their deadline day", () => {
    const weekStart = new Date("2030-01-07T00:00:00");
    const tasks: Task[] = [
      mkTask(1, "Already Scheduled"),
      mkTask(2, "Deadline Task", "2030-01-09T14:00:00"),
      mkTask(3, "No Deadline Task")
    ];
    const scheduledIds = buildScheduledTaskIds([
      {
        id: 99,
        task_id: 1,
        task_name: "Already Scheduled",
        start_time: "2030-01-07T09:00:00",
        end_time: "2030-01-07T10:00:00",
        duration_minutes: 60
      }
    ]);

    const grouped = buildUnscheduledTasksByDay(tasks, weekStart, scheduledIds);
    const mondayTasks = getListForDay(grouped, "2030-01-07");
    const monday: string[] = [];
    for (let i = 0; i < mondayTasks.length; i++) {
      monday.push(mondayTasks[i].name);
    }

    const wednesdayTasks = getListForDay(grouped, "2030-01-09");
    const wednesday: string[] = [];
    for (let i = 0; i < wednesdayTasks.length; i++) {
      wednesday.push(wednesdayTasks[i].name);
    }

    expect(monday).toContain("No Deadline Task");
    expect(wednesday).toContain("Deadline Task");
    expect(monday).not.toContain("Already Scheduled");
  });

  it("returns an empty list for missing day keys", () => {
    const grouped = new Map<string, ScheduledBlock[]>();
    expect(getListForDay(grouped, "2030-01-10")).toEqual([]);
  });
});
