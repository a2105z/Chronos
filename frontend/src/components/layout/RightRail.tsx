import { useState } from "react";
import type { Task } from "../../types/task";
import type { UnscheduledDiagnostic } from "../../types/schedule";
import "./RightRail.css";

interface RightRailProps {
  tasks: Task[];
  unscheduled: UnscheduledDiagnostic[];
  search: string;
  onSearchChange: (value: string) => void;
  onGoPlanner: () => void;
}

function formatDuration(mins: number): string {
  if (mins < 60) {
    return `${mins} min`;
  }
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `${h} hr ${m}m` : `${h} hr`;
}

export function RightRail({
  tasks,
  unscheduled,
  search,
  onSearchChange,
  onGoPlanner
}: RightRailProps) {
  const [tab, setTab] = useState<"priorities" | "tasks">("tasks");

  const upNext = [...tasks].sort((a, b) => b.priority - a.priority)[0] ?? null;
  const priorityTasks = [...tasks].sort((a, b) => b.priority - a.priority).slice(0, 8);

  return (
    <aside className="right-rail" aria-label="Tasks and priorities">
      <div className="rail-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "priorities"}
          className={tab === "priorities" ? "active" : ""}
          onClick={() => setTab("priorities")}
        >
          Priorities
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "tasks"}
          className={tab === "tasks" ? "active" : ""}
          onClick={() => setTab("tasks")}
        >
          Tasks
        </button>
      </div>

      <label className="rail-search">
        <span aria-hidden>⌕</span>
        <input
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search tasks"
        />
      </label>

      {tab === "tasks" ? (
        <>
          {upNext ? (
            <div className="up-next">
              <p className="up-next-label">Up next</p>
              <h3>{upNext.name}</h3>
              <div className="up-next-meta">
                {upNext.deadline ? (
                  <span>Due {new Date(upNext.deadline).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
                ) : (
                  <span>No due date</span>
                )}
                <span>{formatDuration(upNext.estimated_duration_minutes)}</span>
              </div>
              <button type="button" className="rail-primary" onClick={onGoPlanner}>
                Open in planner
              </button>
            </div>
          ) : (
            <div className="up-next empty">
              <p className="up-next-label">Up next</p>
              <p className="muted small">No tasks yet — use Plan with AI or add one under Tasks.</p>
            </div>
          )}

          {unscheduled.length > 0 ? (
            <div className="rail-section">
              <h4>Needs a home</h4>
              <ul className="rail-list">
                {unscheduled.map((u) => (
                  <li key={`${u.task_id}-${u.reason}`}>
                    <strong>{u.task_name}</strong>
                    <span className="rail-chip">{u.reason.replace(/_/g, " ")}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <div className="rail-section">
            <h4>All tasks</h4>
            {tasks.length === 0 ? (
              <p className="muted small">Nothing here yet.</p>
            ) : (
              <ul className="rail-list">
                {tasks.slice(0, 12).map((t) => (
                  <li key={t.id}>
                    <strong>{t.name}</strong>
                    <span className="muted small">{formatDuration(t.estimated_duration_minutes)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      ) : (
        <div className="rail-section">
          <h4>By priority</h4>
          {priorityTasks.length === 0 ? (
            <p className="muted small">Add tasks to see priorities.</p>
          ) : (
            <ul className="rail-list">
              {priorityTasks.map((t) => (
                <li key={t.id}>
                  <strong>{t.name}</strong>
                  <span className="rail-chip">P{t.priority}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </aside>
  );
}
