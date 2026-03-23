/** One day cell in the three-week schedule grid. */

import type { ReactElement } from "react";
import type { Task } from "../../types/task";
import type { ScheduledBlock } from "../../types/schedule";
import { formatTimeFromIso } from "../../utils/dates";

interface CalendarDayColumnProps {
  day: Date;
  isPastDay: boolean;
  dayBlocks: ScheduledBlock[];
  unscheduledTasks: Task[];
}

export function CalendarDayColumn({
  day,
  isPastDay,
  dayBlocks,
  unscheduledTasks,
}: CalendarDayColumnProps) {
  let sectionClassName = "calendar-day";
  if (isPastDay) {
    sectionClassName = "calendar-day calendar-day-past";
  }

  const weekdayLabel = day.toLocaleDateString([], { weekday: "short" });
  const dateLabel = day.toLocaleDateString();

  const hasBlocks = dayBlocks.length > 0;
  const hasUnscheduled = unscheduledTasks.length > 0;
  const isEmpty = !hasBlocks && !hasUnscheduled;

  let emptyMessage = null;
  if (isEmpty) {
    emptyMessage = <p className="calendar-day-empty">No blocks</p>;
  }

  let blockList = null;
  if (hasBlocks) {
    const items: ReactElement[] = [];
    for (let i = 0; i < dayBlocks.length; i++) {
      const block = dayBlocks[i];
      const startLabel = formatTimeFromIso(block.start_time);
      const endLabel = formatTimeFromIso(block.end_time);
      items.push(
        <li key={block.id} className="schedule-block-item">
          <div className="schedule-block-main">
            <strong>{block.task_name}</strong>
            <span>{block.duration_minutes} min</span>
          </div>
          <div className="schedule-block-time">
            {startLabel} - {endLabel}
          </div>
        </li>
      );
    }
    blockList = <ul className="schedule-block-list">{items}</ul>;
  }

  let unscheduledList = null;
  if (hasUnscheduled) {
    const items: ReactElement[] = [];
    for (let i = 0; i < unscheduledTasks.length; i++) {
      const task = unscheduledTasks[i];
      items.push(
        <li key={task.id} className="unscheduled-task-item">
          <strong>{task.name}</strong>
          <span>Unscheduled · {task.estimated_duration_minutes} min</span>
        </li>
      );
    }
    unscheduledList = <ul className="unscheduled-task-list">{items}</ul>;
  }

  return (
    <section className={sectionClassName}>
      <header className="calendar-day-header">
        <strong>{weekdayLabel}</strong>
        <span>{dateLabel}</span>
      </header>
      {emptyMessage}
      {blockList}
      {unscheduledList}
    </section>
  );
}
