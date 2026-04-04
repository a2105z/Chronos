/** Protected blocks and max continuous work constraints. */

import { useEffect, useState } from "react";
import { getConstraints, createConstraint, deleteConstraint } from "../../api/client";
import type { Constraint } from "../../types/constraint";
import { minutesToTimeInput, timeInputToMinutes, WEEKDAY_LABELS } from "../../utils/timeMinutes";
import "./ConstraintsView.css";

export default function ConstraintsView() {
  const [rows, setRows] = useState<Constraint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [protDay, setProtDay] = useState(0);
  const [protStart, setProtStart] = useState("12:00");
  const [protEnd, setProtEnd] = useState("13:00");

  const [maxMinutes, setMaxMinutes] = useState(60);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await getConstraints();
      setRows(res.data);
    } catch {
      setError("Could not load constraints.");
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(function onMount() {
    load();
  }, []);

  async function handleAddProtected(event: React.FormEvent) {
    event.preventDefault();
    const sm = timeInputToMinutes(protStart);
    const em = timeInputToMinutes(protEnd);
    if (em <= sm) {
      setError("Protected block end must be after start.");
      return;
    }
    setError(null);
    try {
      await createConstraint({
        constraint_type: "protected_block",
        day_of_week: protDay,
        start_minutes: sm,
        end_minutes: em,
      });
      await load();
    } catch {
      setError("Could not add protected block.");
    }
  }

  async function handleAddMaxWork(event: React.FormEvent) {
    event.preventDefault();
    if (maxMinutes < 1) {
      setError("Max continuous work must be at least 1 minute.");
      return;
    }
    setError(null);
    try {
      await createConstraint({
        constraint_type: "max_continuous_work",
        value: maxMinutes,
      });
      await load();
    } catch {
      setError("Could not add max continuous work rule.");
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteConstraint(id);
      await load();
    } catch {
      setError("Could not delete constraint.");
    }
  }

  function describeRow(c: Constraint): string {
    if (c.constraint_type === "protected_block") {
      const d = c.day_of_week ?? 0;
      return `${WEEKDAY_LABELS[d]} ${minutesToTimeInput(c.start_minutes ?? 0)}–${minutesToTimeInput(
        c.end_minutes ?? 0
      )}`;
    }
    if (c.constraint_type === "max_continuous_work") {
      return `Max continuous work: ${c.value ?? "?"} min`;
    }
    return c.constraint_type;
  }

  if (loading) {
    return <div className="panel-view">Loading constraints…</div>;
  }

  return (
    <div className="panel-view constraints-view">
      <div className="panel-header">
        <h2>Constraints</h2>
        <p className="panel-lead">
          Protected blocks keep tasks out (e.g. lunch). Max continuous work splits sessions so no single block
          exceeds the limit.
        </p>
      </div>

      {error !== null ? <p className="form-error-banner">{error}</p> : null}

      <section className="constraint-section">
        <h3>Protected time</h3>
        <form className="stacked-form" onSubmit={handleAddProtected}>
          <label>
            Day
            <select value={protDay} onChange={(e) => setProtDay(parseInt(e.target.value, 10))}>
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
              <input type="time" value={protStart} onChange={(e) => setProtStart(e.target.value)} />
            </label>
            <label>
              End
              <input type="time" value={protEnd} onChange={(e) => setProtEnd(e.target.value)} />
            </label>
          </div>
          <button type="submit" className="btn-primary">
            Add protected block
          </button>
        </form>
      </section>

      <section className="constraint-section">
        <h3>Max continuous work</h3>
        <form className="stacked-form max-work-form" onSubmit={handleAddMaxWork}>
          <label>
            Minutes per block (minimum 1)
            <input
              type="number"
              min={1}
              value={maxMinutes}
              onChange={(e) => setMaxMinutes(parseInt(e.target.value, 10) || 1)}
            />
          </label>
          <button type="submit" className="btn-primary">
            Add rule
          </button>
        </form>
      </section>

      <h3>Active constraints</h3>
      <ul className="constraints-list">
        {rows.length === 0 ? <li className="muted">No constraints configured.</li> : null}
        {rows.map((c) => (
          <li key={c.id} className="constraints-row">
            <span>
              <strong>{c.constraint_type}</strong>
              <span className="muted"> · {describeRow(c)}</span>
            </span>
            <button type="button" className="btn-danger btn-compact" onClick={() => handleDelete(c.id)}>
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
