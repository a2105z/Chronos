import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { planWithAi, getSuggestions } from "../../api/client";
import type { AiPlanResponse } from "../../types/app";
import type { UnscheduledDiagnostic } from "../../types/schedule";
import { addDays, getStartOfWeekMonday } from "../../utils/calendarGrid";
import { toIsoDateTime } from "../../utils/dates";
import "./PlanView.css";

const EXAMPLE_CHIPS = [
  "Find me 3 spots, each 2 hours long for deep work",
  "Schedule 3 hours of deep work on the Chronos resume tomorrow morning, high priority",
  "I have a test for STAT 410 on Thursday at 5-6:30. Block out per day to study",
  "I'm free weekdays 9am to 5pm"
];

interface PlanViewProps {
  onPlanned?: () => void;
}

export default function PlanView({ onPlanned }: PlanViewProps) {
  const [prompt, setPrompt] = useState("");
  const [focused, setFocused] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AiPlanResponse | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    getSuggestions()
      .then((res) => setSuggestions(res.data.suggestions))
      .catch(() => setSuggestions([]));
  }, []);

  async function runPlan(event?: FormEvent) {
    if (event) {
      event.preventDefault();
    }
    if (!prompt.trim()) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const monday = getStartOfWeekMonday();
      const start = toIsoDateTime(monday);
      const end = toIsoDateTime(addDays(monday, 7));
      const res = await planWithAi(prompt.trim(), start, end, true);
      setResult(res.data);
      onPlanned?.();
    } catch {
      setError("Could not plan that prompt. Is the API running?");
    } finally {
      setBusy(false);
    }
  }

  const diagnostics: UnscheduledDiagnostic[] = result?.schedule?.unscheduled ?? [];

  return (
    <section className="plan-view">
      <div className={`plan-hero ${focused ? "is-focused" : ""}`}>
        <p className="brand-hero">Chronos</p>
        <p className="plan-lead plan-lead-hero">
          Describe the week in plain English. Chronos places constraint-verified blocks — and explains anything that cannot fit.
        </p>

        <form className="plan-composer" onSubmit={runPlan}>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="e.g. Schedule 3 hours of deep work on the Chronos resume tomorrow morning, high priority"
            rows={4}
            aria-label="Planning prompt"
          />
          <div className="composer-actions">
            <button type="submit" className="btn-primary" disabled={busy || !prompt.trim()}>
              {busy ? "Planning…" : "Plan my week"}
            </button>
          </div>
        </form>

        <div className="chip-row" aria-label="Example prompts">
          {EXAMPLE_CHIPS.map((chip) => (
            <button
              key={chip}
              type="button"
              className="chip"
              onClick={() => setPrompt(chip)}
            >
              {chip}
            </button>
          ))}
        </div>
      </div>

      {error ? <p className="plan-error">{error}</p> : null}

      {result ? (
        <div className="plan-result fade-in">
          <h2>Plan result</h2>
          <p className="assistant-message">{result.assistant_message}</p>
          <p className="muted small">
            Parser: {result.intent.parser}
            {result.created.tasks.length > 0
              ? ` · created ${result.created.tasks.map((t) => t.name || "task").join(", ")}`
              : ""}
          </p>
          {result.schedule ? (
            <p className="schedule-summary">{result.schedule.summary}</p>
          ) : null}
          <p className="muted small">Open Calendar to review the week grid, drag blocks, and export .ics.</p>
          {diagnostics.length > 0 ? (
            <div className="diagnostics">
              <h3>Unscheduled</h3>
              <ul>
                {diagnostics.map((d) => (
                  <li key={`${d.task_id}-${d.reason}`}>
                    <strong>{d.task_name}</strong>
                    <span className="reason-pill">{d.reason}</span>
                    <span className="detail">{d.detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}

      {suggestions.length > 0 ? (
        <div className="suggestions">
          <h2>Suggestions</h2>
          <ul>
            {suggestions.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
