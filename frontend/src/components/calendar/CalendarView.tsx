/** Weekly schedule: load persisted blocks, regenerate, move/delete with server validation, export .ics. */

import { useEffect, useState } from "react";
import type { ReactElement } from "react";
import axios from "axios";
import {
  deleteScheduleBlock,
  exportSchedule,
  generateSchedule,
  getSchedule,
  getTasks,
  moveScheduleBlock,
} from "../../api/client";
import type { Task } from "../../types/task";
import type { ScheduledBlock } from "../../types/schedule";
import {
  fromDatetimeLocalToIso,
  toDatetimeLocalValue,
  toIsoDateTime,
  triggerBlobDownload,
} from "../../utils/dates";
import { addDays, getDateKey, getWeekDaysFromMonday } from "../../utils/calendarGrid";
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
  weekMonday: Date;
  onWeekChange: (nextMonday: Date) => void;
}

function weekKey(monday: Date): string {
  return getDateKey(monday);
}

export default function CalendarView({ refreshTrigger = 0, weekMonday, onWeekChange }: CalendarViewProps) {
  const [blocks, setBlocks] = useState<ScheduledBlock[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [moveError, setMoveError] = useState<string | null>(null);
  const [movingBlock, setMovingBlock] = useState<ScheduledBlock | null>(null);
  const [moveStartLocal, setMoveStartLocal] = useState("");

  const rangeEndExclusive = addDays(weekMonday, 7);
  const startIso = toIsoDateTime(weekMonday);
  const endIso = toIsoDateTime(rangeEndExclusive);
  const weekDays = getWeekDaysFromMonday(weekMonday, 7);

  async function syncWeekData(
    source: "persisted" | "regenerate",
    onErrorMessage: string
  ) {
    setLoading(true);
    setError(null);
    try {
      const scheduleRequest =
        source === "regenerate"
          ? generateSchedule(startIso, endIso)
          : getSchedule(startIso, endIso);
      const [scheduleRes, tasksRes] = await Promise.all([scheduleRequest, getTasks()]);
      setBlocks(scheduleRes.data);
      setTasks(tasksRes.data);
    } catch {
      setError(onErrorMessage);
      setBlocks([]);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }

  async function loadPersistedSchedule() {
    await syncWeekData("persisted", "Failed to load schedule. Is the API running?");
  }

  async function handleRegenerate() {
    await syncWeekData("regenerate", "Could not regenerate schedule.");
  }

  async function handleExport() {
    setError(null);
    try {
      const res = await exportSchedule(startIso, endIso);
      triggerBlobDownload(res.data, "chronos_schedule.ics");
    } catch {
      setError("Export failed.");
    }
  }

  useEffect(
    function reloadOnDeps() {
      loadPersistedSchedule();
    },
    [refreshTrigger, weekKey(weekMonday)]
  );

  function openMove(block: ScheduledBlock) {
    setMoveError(null);
    setMovingBlock(block);
    setMoveStartLocal(toDatetimeLocalValue(block.start_time));
  }

  function closeMove() {
    setMovingBlock(null);
    setMoveError(null);
  }

  async function submitMove(event: React.FormEvent) {
    event.preventDefault();
    if (movingBlock === null) {
      return;
    }
    setMoveError(null);
    try {
      const iso = fromDatetimeLocalToIso(moveStartLocal);
      await moveScheduleBlock(movingBlock.id, iso);
      closeMove();
      await loadPersistedSchedule();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        const detail = err.response.data?.detail;
        setMoveError(typeof detail === "string" ? detail : "That move is not allowed.");
      } else {
        setMoveError("Could not move this block.");
      }
    }
  }

  async function handleDeleteBlock(blockId: number) {
    if (!window.confirm("Remove this scheduled block?")) {
      return;
    }
    setError(null);
    try {
      await deleteScheduleBlock(blockId);
      await loadPersistedSchedule();
    } catch {
      setError("Could not delete that block.");
    }
  }

  const blocksByDay = buildBlocksByDay(blocks);
  const scheduledTaskIds = buildScheduledTaskIds(blocks);
  const unscheduledByDay = buildUnscheduledTasksByDay(tasks, weekMonday, scheduledTaskIds);

  const todayMidnight = new Date();
  todayMidnight.setHours(0, 0, 0, 0);

  const dayColumns: ReactElement[] = [];
  for (let i = 0; i < weekDays.length; i++) {
    const day = weekDays[i];
    const dayKey = getDateKey(day);
    const dayBlocks = getListForDay(blocksByDay, dayKey);
    const unscheduledTasks = getListForDay(unscheduledByDay, dayKey);
    const isPastDay = day < todayMidnight;
    dayColumns.push(
      <CalendarDayColumn
        key={dayKey}
        day={day}
        isPastDay={isPastDay}
        dayBlocks={dayBlocks}
        unscheduledTasks={unscheduledTasks}
        onMoveBlock={openMove}
        onDeleteBlock={handleDeleteBlock}
      />
    );
  }

  let refreshLabel = "Refresh";
  if (loading) {
    refreshLabel = "Loading…";
  }

  let errorSection: ReactElement | null = null;
  if (error !== null) {
    errorSection = <p className="calendar-error">{error}</p>;
  }

  const gridSection = (
    <div className="week-grid-wrap">
      <div className="week-grid">{dayColumns}</div>
    </div>
  );

  let moveOverlay: ReactElement | null = null;
  if (movingBlock !== null) {
    moveOverlay = (
      <div className="move-overlay" role="dialog" aria-modal="true">
        <form className="move-dialog" onSubmit={submitMove}>
          <h3>Move block</h3>
          <p className="muted small">
            {movingBlock.task_name} · duration stays {movingBlock.duration_minutes} min. Invalid moves are rejected
            by the server.
          </p>
          <label>
            New start (local)
            <input
              type="datetime-local"
              value={moveStartLocal}
              onChange={(e) => setMoveStartLocal(e.target.value)}
              required
            />
          </label>
          {moveError !== null ? <p className="calendar-error">{moveError}</p> : null}
          <div className="move-actions">
            <button type="button" className="btn-secondary" onClick={closeMove}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save move
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="calendar-view">
      {moveOverlay}
      <div className="calendar-header">
        <h2>Week of {weekMonday.toLocaleDateString()}</h2>
        <div className="calendar-toolbar">
          <button type="button" className="btn-secondary" onClick={() => onWeekChange(addDays(weekMonday, -7))}>
            ← Prev
          </button>
          <button type="button" className="btn-secondary" onClick={() => onWeekChange(addDays(weekMonday, 7))}>
            Next →
          </button>
          <button type="button" className="btn-primary" onClick={loadPersistedSchedule} disabled={loading}>
            {refreshLabel}
          </button>
          <button type="button" className="btn-primary" onClick={handleRegenerate} disabled={loading}>
            Regenerate
          </button>
          <button type="button" className="btn-secondary" onClick={handleExport} disabled={loading}>
            Export .ics
          </button>
        </div>
      </div>

      {blocks.length === 0 && !loading ? (
        <p className="calendar-hint">
          No blocks saved for this week yet. Regenerate runs the scheduler and stores the result so you can move or
          delete blocks.
        </p>
      ) : null}

      {errorSection}
      {gridSection}
    </div>
  );
}
