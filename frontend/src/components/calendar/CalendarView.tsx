import { useEffect, useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import type {
  DateSelectArg,
  EventClickArg,
  EventContentArg,
  EventDropArg,
  EventInput
} from "@fullcalendar/core";
import type { EventResizeDoneArg } from "@fullcalendar/interaction";
import {
  createScheduleBlock,
  deleteScheduleBlock,
  explainSchedule,
  exportSchedule,
  generateSchedule,
  getSchedule,
  moveScheduleBlock
} from "../../api/client";
import type { ScheduledBlock, UnscheduledDiagnostic } from "../../types/schedule";
import { addDays, getStartOfWeekMonday } from "../../utils/calendarGrid";
import { toLocalApiDateTime, toIsoDateTime, triggerBlobDownload } from "../../utils/dates";
import { colorForTitle } from "../../utils/eventColors";
import "./CalendarView.css";

interface CalendarViewProps {
  refreshTrigger?: number;
  weekMonday: Date;
  onWeekChange: (nextMonday: Date) => void;
  onUnscheduledChange?: (items: UnscheduledDiagnostic[]) => void;
  embed?: boolean;
}

interface SelectedBlock {
  id: number;
  title: string;
  start: string;
  end: string;
}

function formatRangeLabel(monday: Date): string {
  return monday.toLocaleDateString(undefined, { month: "long", year: "numeric" });
}

function formatEventTime(start: Date | null, end: Date | null): string {
  if (!start || !end) {
    return "";
  }
  const opts: Intl.DateTimeFormatOptions = { hour: "numeric", minute: "2-digit" };
  return `${start.toLocaleTimeString(undefined, opts)} – ${end.toLocaleTimeString(undefined, opts)}`;
}

function hoursBetween(startIso: string, endIso: string): number {
  return Math.max(0, (new Date(endIso).getTime() - new Date(startIso).getTime()) / 3600000);
}

function extractApiDetail(err: unknown): string | null {
  if (err && typeof err === "object" && "response" in err) {
    const response = (err as { response?: { data?: { detail?: unknown } } }).response;
    const detail = response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }
  return null;
}

function isPastLocal(date: Date): boolean {
  return date.getTime() < Date.now();
}

export default function CalendarView({
  refreshTrigger = 0,
  weekMonday,
  onWeekChange,
  onUnscheduledChange,
  embed = false
}: CalendarViewProps) {
  const [blocks, setBlocks] = useState<ScheduledBlock[]>([]);
  const [unscheduled, setUnscheduled] = useState<UnscheduledDiagnostic[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [selected, setSelected] = useState<SelectedBlock | null>(null);

  const rangeEnd = useMemo(() => addDays(weekMonday, 7), [weekMonday]);
  const startIso = useMemo(() => toIsoDateTime(weekMonday), [weekMonday]);
  const endIso = useMemo(() => toIsoDateTime(rangeEnd), [rangeEnd]);

  const legend = useMemo(() => {
    const map = new Map<string, { label: string; color: string; hours: number }>();
    for (const b of blocks) {
      const c = colorForTitle(b.task_name);
      const prev = map.get(c.key);
      const hours = hoursBetween(b.start_time, b.end_time);
      if (prev) {
        prev.hours += hours;
      } else {
        map.set(c.key, { label: c.label, color: c.bg, hours });
      }
    }
    return Array.from(map.values()).sort((a, b) => b.hours - a.hours).slice(0, 6);
  }, [blocks]);

  const totalHours = legend.reduce((sum, l) => sum + l.hours, 0);

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 2800);
  }

  async function loadPersisted() {
    setLoading(true);
    setError(null);
    try {
      const [scheduleRes, explainRes] = await Promise.all([
        getSchedule(startIso, endIso),
        explainSchedule(startIso, endIso)
      ]);
      setBlocks(scheduleRes.data);
      setUnscheduled(explainRes.data.unscheduled);
      onUnscheduledChange?.(explainRes.data.unscheduled);
      setSummary(explainRes.data.summary);
    } catch {
      setError("Couldn’t load your calendar. Is the API running?");
      setBlocks([]);
      setUnscheduled([]);
      onUnscheduledChange?.([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegenerate() {
    setLoading(true);
    setError(null);
    setSelected(null);
    try {
      const res = await generateSchedule(startIso, endIso, true);
      setBlocks(res.data.blocks);
      setUnscheduled(res.data.unscheduled);
      onUnscheduledChange?.(res.data.unscheduled);
      setSummary(res.data.summary);
      showToast("Week rebuilt");
    } catch {
      setError("Could not regenerate schedule.");
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    try {
      const res = await exportSchedule(startIso, endIso);
      triggerBlobDownload(res.data, "chronos_schedule.ics");
      showToast("Exported .ics");
    } catch {
      setError("Export failed.");
    }
  }

  useEffect(() => {
    loadPersisted();
  }, [refreshTrigger, startIso, endIso]);

  const events: EventInput[] = blocks.map((b) => {
    const c = colorForTitle(b.task_name);
    return {
      id: String(b.id),
      title: b.task_name,
      start: b.start_time,
      end: b.end_time,
      backgroundColor: c.bg,
      borderColor: c.border,
      textColor: c.text,
      editable: true,
      durationEditable: true,
      startEditable: true,
      extendedProps: { blockId: b.id, soft: c.soft }
    };
  });

  async function onEventDrop(info: EventDropArg) {
    const blockId = Number(info.event.extendedProps.blockId || info.event.id);
    if (!info.event.start || !info.event.end) {
      info.revert();
      return;
    }
    if (isPastLocal(info.event.start)) {
      info.revert();
      setError("That time has already passed — try a time in the future (CST).");
      return;
    }
    try {
      await moveScheduleBlock(
        blockId,
        toLocalApiDateTime(info.event.start),
        toLocalApiDateTime(info.event.end)
      );
      setSelected(null);
      showToast("Moved");
      await loadPersisted();
    } catch (err) {
      info.revert();
      const detail = extractApiDetail(err);
      setError(detail || "That spot doesn’t work — overlaps or outside availability.");
    }
  }

  async function onEventResize(info: EventResizeDoneArg) {
    const blockId = Number(info.event.extendedProps.blockId || info.event.id);
    if (!info.event.start || !info.event.end) {
      info.revert();
      return;
    }
    if (isPastLocal(info.event.start)) {
      info.revert();
      setError("That time has already passed — try a time in the future (CST).");
      return;
    }
    try {
      await moveScheduleBlock(
        blockId,
        toLocalApiDateTime(info.event.start),
        toLocalApiDateTime(info.event.end)
      );
      setSelected(null);
      showToast("Resized");
      await loadPersisted();
    } catch (err) {
      info.revert();
      const detail = extractApiDetail(err);
      setError(detail || "Couldn’t resize there — try a different length or time.");
    }
  }

  function onEventClick(info: EventClickArg) {
    info.jsEvent.preventDefault();
    if (!info.event.start || !info.event.end) {
      return;
    }
    setSelected({
      id: Number(info.event.extendedProps.blockId || info.event.id),
      title: info.event.title,
      start: info.event.start.toISOString(),
      end: info.event.end.toISOString()
    });
    setError(null);
  }

  async function onSelect(info: DateSelectArg) {
    if (isPastLocal(info.start)) {
      info.view.calendar.unselect();
      setError("That time has already passed — try a time in the future (CST).");
      return;
    }
    const title = window.prompt("What should we block?", "Focus time");
    info.view.calendar.unselect();
    if (!title || !title.trim()) {
      return;
    }
    try {
      await createScheduleBlock(
        title.trim(),
        toLocalApiDateTime(info.start),
        toLocalApiDateTime(info.end)
      );
      showToast("Block added");
      await loadPersisted();
    } catch (err) {
      const detail = extractApiDetail(err);
      setError(detail || "Couldn’t create that block. Check availability and overlaps.");
    }
  }

  async function handleDeleteSelected() {
    if (!selected) {
      return;
    }
    try {
      await deleteScheduleBlock(selected.id);
      setSelected(null);
      showToast("Removed");
      await loadPersisted();
    } catch {
      setError("Could not delete that block.");
    }
  }

  function renderEventContent(arg: EventContentArg) {
    const soft = Boolean(arg.event.extendedProps.soft);
    const time = formatEventTime(arg.event.start, arg.event.end);
    return (
      <div className={`gcal-event ${soft ? "soft" : ""}`}>
        <div className="gcal-event-title">{arg.event.title}</div>
        {time ? <div className="gcal-event-time">{time}</div> : null}
      </div>
    );
  }

  return (
    <div className={`calendar-view fade-in ${embed ? "embed" : ""}`}>
      <div className="calendar-header">
        <div className="calendar-heading">
          <div className="planner-title-row">
            <h2>Planner</h2>
            <div className="month-nav">
              <button type="button" className="icon-nav" onClick={() => onWeekChange(addDays(weekMonday, -7))} aria-label="Previous week">
                ‹
              </button>
              <button type="button" className="month-label" onClick={() => onWeekChange(getStartOfWeekMonday())}>
                {formatRangeLabel(weekMonday)}
              </button>
              <button type="button" className="icon-nav" onClick={() => onWeekChange(addDays(weekMonday, 7))} aria-label="Next week">
                ›
              </button>
            </div>
          </div>
          <p className="calendar-hint">
            Drag to move · resize edges · drag empty time to add · times are CST — past slots aren’t allowed
          </p>
        </div>
        <div className="calendar-toolbar">
          <button type="button" className="btn-today" onClick={() => onWeekChange(getStartOfWeekMonday())}>
            Today
          </button>
          <button type="button" className="btn-secondary" onClick={loadPersisted} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </button>
          <button type="button" className="btn-primary" onClick={handleRegenerate} disabled={loading}>
            Auto-plan
          </button>
          <button type="button" className="btn-secondary" onClick={handleExport} disabled={loading}>
            Export
          </button>
        </div>
      </div>

      {legend.length > 0 ? (
        <div className="legend-bar" aria-label="Time breakdown">
          <div className="legend-track">
            {legend.map((l) => (
              <div
                key={l.label}
                className="legend-seg"
                style={{
                  background: l.color,
                  flexGrow: Math.max(l.hours, 0.35)
                }}
                title={`${l.label}: ${l.hours.toFixed(1)}h`}
              />
            ))}
            {totalHours < 40 ? (
              <div className="legend-seg free" style={{ flexGrow: Math.max(40 - totalHours, 1) }} title="Free" />
            ) : null}
          </div>
          <div className="legend-labels">
            {legend.map((l) => (
              <span key={l.label}>
                <i style={{ background: l.color }} />
                {l.label} {l.hours.toFixed(1)}h
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="calendar-banner error" role="alert">
          {error}
          <button type="button" className="banner-dismiss" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      ) : null}
      {toast ? <div className="calendar-banner toast">{toast}</div> : null}
      {summary && !embed ? <p className="muted small">{summary}</p> : null}

      <div className={`calendar-layout ${embed ? "embed-layout" : ""}`}>
        <div className={`fc-wrap gcal ${loading ? "is-loading" : ""}`}>
          <FullCalendar
            plugins={[timeGridPlugin, interactionPlugin]}
            initialView="timeGridWeek"
            headerToolbar={false}
            initialDate={weekMonday}
            key={weekMonday.toISOString()}
            events={events}
            editable
            eventStartEditable
            eventDurationEditable
            eventResizableFromStart
            selectable
            selectMirror
            selectOverlap={false}
            eventOverlap={false}
            snapDuration="00:15:00"
            slotDuration="00:30:00"
            slotLabelInterval="01:00:00"
            dragScroll
            eventDrop={onEventDrop}
            eventResize={onEventResize}
            eventClick={onEventClick}
            select={onSelect}
            eventContent={renderEventContent}
            height="auto"
            expandRows
            slotMinTime="07:00:00"
            slotMaxTime="22:00:00"
            allDaySlot={false}
            nowIndicator
            weekends
            dayHeaderFormat={{ weekday: "short", day: "numeric" }}
            slotLabelFormat={{ hour: "numeric", meridiem: "short" }}
          />
        </div>

        {!embed ? (
          <aside className="calendar-rail">
            {selected ? (
              <div className="block-sheet">
                <h3>{selected.title}</h3>
                <p className="muted small">
                  {formatEventTime(new Date(selected.start), new Date(selected.end))}
                </p>
                <div className="sheet-actions">
                  <button type="button" className="btn-secondary" onClick={() => setSelected(null)}>
                    Done
                  </button>
                  <button type="button" className="btn-danger" onClick={handleDeleteSelected}>
                    Delete
                  </button>
                </div>
              </div>
            ) : null}
            <div className="unscheduled-sidebar">
              <h3>Needs a home</h3>
              {unscheduled.length === 0 ? (
                <p className="muted small">Everything fits.</p>
              ) : (
                <ul>
                  {unscheduled.map((u) => (
                    <li key={`${u.task_id}-${u.reason}`}>
                      <strong>{u.task_name}</strong>
                      <span className="reason-pill">{u.reason.replace(/_/g, " ")}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </aside>
        ) : selected ? (
          <div className="block-sheet floating">
            <h3>{selected.title}</h3>
            <p className="muted small">
              {formatEventTime(new Date(selected.start), new Date(selected.end))}
            </p>
            <div className="sheet-actions">
              <button type="button" className="btn-secondary" onClick={() => setSelected(null)}>
                Done
              </button>
              <button type="button" className="btn-danger" onClick={handleDeleteSelected}>
                Delete
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
