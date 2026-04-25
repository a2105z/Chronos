import { useEffect, useState } from "react";
import type { ReactElement } from "react";
import {
  getAvailability,
  createAvailability,
  deleteAvailability
} from "../../api/client";
import type { Availability } from "../../types/availability";
import { minutesToTimeInput, timeInputToMinutes, WEEKDAY_LABELS } from "../../utils/timeMinutes";
import "./AvailabilityView.css";

export default function AvailabilityView() {
  const [rows, setRows] = useState<Availability[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dayOfWeek, setDayOfWeek] = useState(0);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("17:00");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      let res = await getAvailability();
      setRows(res.data);
    } catch {
      setError("Could not load availability.");
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(function onMount() {
    load();
  }, []);

  async function handleAdd(event: React.FormEvent) {
    event.preventDefault();
    let startMinutes = timeInputToMinutes(startTime);
    let endMinutes = timeInputToMinutes(endTime);
    if (endMinutes <= startMinutes) {
      setError("End time must be after start time.");
      return;
    }
    setError(null);
    try {
      await createAvailability({
        day_of_week: dayOfWeek,
        start_minutes: startMinutes,
        end_minutes: endMinutes
      });
      await load();
    } catch {
      setError("Could not save this window.");
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteAvailability(id);
      await load();
    } catch {
      setError("Could not delete that window.");
    }
  }

  if (loading) {
    return <div className="panel-view">Loading availability…</div>;
  }

  let errorBanner: ReactElement | null = null;
  if (error !== null) {
    errorBanner = <p className="form-error-banner">{error}</p>;
  }

  let emptyRow: ReactElement | null = null;
  if (rows.length === 0) {
    emptyRow = <li className="muted">No windows yet. Add at least one, or the scheduler uses a full-week fallback.</li>;
  }

  let weekdayOptions: ReactElement[] = [];
  for (let idx = 0; idx < WEEKDAY_LABELS.length; idx++) {
    let label = WEEKDAY_LABELS[idx];
    weekdayOptions.push(
      <option key={label} value={idx}>
        {label}
      </option>
    );
  }

  let availabilityRows: ReactElement[] = [];
  for (let i = 0; i < rows.length; i++) {
    let windowRow = rows[i];
    availabilityRows.push(
      <li key={windowRow.id} className="availability-row">
        <div>
          <strong>{WEEKDAY_LABELS[windowRow.day_of_week] ?? `Day ${windowRow.day_of_week}`}</strong>
          <span className="muted">
            {" "}
            {minutesToTimeInput(windowRow.start_minutes)} – {minutesToTimeInput(windowRow.end_minutes)}
          </span>
        </div>
        <button type="button" className="btn-danger btn-compact" onClick={() => handleDelete(windowRow.id)}>
          Remove
        </button>
      </li>
    );
  }

  return (
    <div className="panel-view availability-view">
      <div className="panel-header">
        <h2>Availability</h2>
        <p className="panel-lead">
          Recurring weekly windows when Chronos may schedule work (e.g. Mon 9:00–17:00). Day 0 is Monday.
        </p>
      </div>

      {errorBanner}

      <form className="stacked-form" onSubmit={handleAdd}>
        <label>
          Day
          <select value={dayOfWeek} onChange={(e) => setDayOfWeek(parseInt(e.target.value, 10))}>
            {weekdayOptions}
          </select>
        </label>
        <div className="inline-time-row">
          <label>
            Start
            <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} required />
          </label>
          <label>
            End
            <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} required />
          </label>
        </div>
        <button type="submit" className="btn-primary">
          Add window
        </button>
      </form>

      <ul className="availability-list">
        {emptyRow}
        {availabilityRows}
      </ul>
    </div>
  );
}
