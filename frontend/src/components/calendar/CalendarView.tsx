/** Three-week schedule view: loads blocks and shows per-day layout. */

import { useEffect, useState } from "react";
import type { ReactElement } from "react";
import { generateSchedule, getTasks } from "../../api/client";
import type { Task } from "../../types/task";
import type { ScheduledBlock } from "../../types/schedule";
import { toIsoDateTime } from "../../utils/dates";
import {
  getStartOfCurrentWeek,
  getDateKey,
  getThreeWeekDays,
} from "../../utils/calendarGrid";
import {
  buildBlocksByDay,
  buildScheduledTaskIds,
  buildUnscheduledTasksByDay,
  getListForDay,
} from "../../utils/scheduleMaps";
import { CalendarDayColumn } from "./CalendarDayColumn";
import "./CalendarView.css";

interface CalendarViewProps {
  refreshTrigger?: number;
}

export default function CalendarView({ refreshTrigger = 0 }: CalendarViewProps) {
  const [blocks, setBlocks] = useState<ScheduledBlock[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const weekStart = getStartOfCurrentWeek();
  const threeWeekDays = getThreeWeekDays(weekStart);

  async function loadSchedule() {
    setLoading(true);
    setError(null);
    try {
      const rangeStart = new Date(weekStart);
      const now = new Date();
      if (now > rangeStart) {
        rangeStart.setTime(now.getTime());
      }

      const rangeEnd = new Date(weekStart);
      rangeEnd.setDate(rangeEnd.getDate() + 21);

      const scheduleResponse = await generateSchedule(
        toIsoDateTime(rangeStart),
        toIsoDateTime(rangeEnd)
      );
      const tasksResponse = await getTasks();

      setBlocks(scheduleResponse.data);
      setTasks(tasksResponse.data);
    } catch {
      setError("Failed to load schedule. Please try again.");
      setBlocks([]);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(function reloadWhenTriggerChanges() {
    loadSchedule();
  }, [refreshTrigger]);

  const blocksByDay = buildBlocksByDay(blocks);
  const scheduledTaskIds = buildScheduledTaskIds(blocks);
  const unscheduledByDay = buildUnscheduledTasksByDay(tasks, weekStart, scheduledTaskIds);

  const todayMidnight = new Date();
  todayMidnight.setHours(0, 0, 0, 0);

  let refreshButtonLabel = "Refresh Schedule";
  if (loading) {
    refreshButtonLabel = "Loading...";
  }

  let errorSection: ReactElement | null = null;
  if (error !== null) {
    errorSection = <p className="calendar-error">{error}</p>;
  }

  const dayColumns: ReactElement[] = [];
  for (let i = 0; i < threeWeekDays.length; i++) {
    const day = threeWeekDays[i];
    const dayKey = getDateKey(day);
    const dayBlocks = getListForDay(blocksByDay, dayKey);
    const unscheduledTasks = getListForDay(unscheduledByDay, dayKey);
    let isPastDay = false;
    if (day < todayMidnight) {
      isPastDay = true;
    }
    dayColumns.push(
      <CalendarDayColumn
        key={dayKey}
        day={day}
        isPastDay={isPastDay}
        dayBlocks={dayBlocks}
        unscheduledTasks={unscheduledTasks}
      />
    );
  }

  let gridSection: ReactElement | null = null;
  if (!loading && error === null) {
    gridSection = (
      <div className="three-week-grid-wrap">
        <div className="three-week-grid">{dayColumns}</div>
      </div>
    );
  }

  return (
    <div className="calendar-view">
      <div className="calendar-header">
        <h2>Schedule</h2>
        <button className="btn-primary" type="button" onClick={loadSchedule} disabled={loading}>
          {refreshButtonLabel}
        </button>
      </div>

      {errorSection}
      {gridSection}
    </div>
  );
}
