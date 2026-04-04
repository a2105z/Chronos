/** CRUD for weekly availability windows (matches backend day_of_week 0=Monday). */

import { useEffect, useState } from "react";
import {
  getAvailability,
  createAvailability,
  deleteAvailability,
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
      const res = await getAvailability();
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
    const startMinutes = timeInputToMinutes(startTime);
    const endMinutes = timeInputToMinutes(endTime);
    if (endMinutes <= startMinutes) {
      setError("End time must be after start time.");
      return;
    }
    setError(null);
    try {
      await createAvailability({
        day_of_week: dayOfWeek,
        start_minutes: startMinutes,
        end_minutes: endMinutes,
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

  return (
    <div className="panel-view availability-view">
      <div className="panel-header">
        <h2>Availability</h2>
        <p className="panel-lead">
          Recurring weekly windows when Chronos may schedule work (e.g. Mon 9:00–17:00). Day 0 is Monday.
        </p>
      </div>

      {error !== null ? <p className="form-error-banner">{error}</p> : null}

      <form className="stacked-form" onSubmit={handleAdd}>
        <label>
          Day
          <select value={dayOfWeek} onChange={(e) => setDayOfWeek(parseInt(e.target.value, 10))}>
            {WEEKDAY_LABELS.map((label, idx) => (
              <option key={label} value={idx}>
                {label}
              </option>
            ))}
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
        {rows.length === 0 ? (
          <li className="muted">No windows yet. Add at least one, or the scheduler uses a full-week fallback.</li>
        ) : null}
        {rows.map((w) => (
          <li key={w.id} className="availability-row">
            <div>
              <strong>{WEEKDAY_LABELS[w.day_of_week] ?? `Day ${w.day_of_week}`}</strong>
              <span className="muted">
                {" "}
                {minutesToTimeInput(w.start_minutes)} – {minutesToTimeInput(w.end_minutes)}
              </span>
            </div>
            <button type="button" className="btn-danger btn-compact" onClick={() => handleDelete(w.id)}>
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
