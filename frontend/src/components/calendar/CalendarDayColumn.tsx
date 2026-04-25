import type { ReactElement } from "react";
import type { Task } from "../../types/task";
import type { ScheduledBlock } from "../../types/schedule";
import { formatTimeFromIso } from "../../utils/dates";

interface CalendarDayColumnProps {
  day: Date;
  isPastDay: boolean;
  dayBlocks: ScheduledBlock[];
  unscheduledTasks: Task[];
  onMoveBlock?: (block: ScheduledBlock) => void;
  onDeleteBlock?: (blockId: number) => void;
}

export function CalendarDayColumn({
  day,
  isPastDay,
  dayBlocks,
  unscheduledTasks,
  onMoveBlock,
  onDeleteBlock
}: CalendarDayColumnProps) {
  let sectionClassName = "calendar-day";
  if (isPastDay) {
    sectionClassName = "calendar-day calendar-day-past";
  }

  let weekdayLabel = day.toLocaleDateString([], { weekday: "short" });
  let dateLabel = day.toLocaleDateString();

  let hasBlocks = dayBlocks.length > 0;
  let hasUnscheduled = unscheduledTasks.length > 0;
  let isEmpty = !hasBlocks && !hasUnscheduled;

  let emptyMessage = null;
  if (isEmpty) {
    emptyMessage = <p className="calendar-day-empty">No blocks</p>;
  }

  let canEditBlocks = !isPastDay && onMoveBlock !== undefined && onDeleteBlock !== undefined;

  let blockList = null;
  if (hasBlocks) {
    let items: ReactElement[] = [];
    for (let i = 0; i < dayBlocks.length; i++) {
      let block = dayBlocks[i];
      let startLabel = formatTimeFromIso(block.start_time);
      let endLabel = formatTimeFromIso(block.end_time);
      let actions: ReactElement | null = null;
      if (canEditBlocks) {
        actions = (
          <div className="schedule-block-actions">
            <button type="button" className="btn-link" onClick={() => onMoveBlock(block)}>
              Move
            </button>
            <button type="button" className="btn-link danger" onClick={() => onDeleteBlock(block.id)}>
              Delete
            </button>
          </div>
        );
      }
      items.push(
        <li key={block.id} className="schedule-block-item">
          <div className="schedule-block-main">
            <strong>{block.task_name}</strong>
            <span>{block.duration_minutes} min</span>
          </div>
          <div className="schedule-block-time">
            {startLabel} - {endLabel}
          </div>
          {actions}
        </li>
      );
    }
    blockList = <ul className="schedule-block-list">{items}</ul>;
  }

  let unscheduledList = null;
  if (hasUnscheduled) {
    let items: ReactElement[] = [];
    for (let i = 0; i < unscheduledTasks.length; i++) {
      let task = unscheduledTasks[i];
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
