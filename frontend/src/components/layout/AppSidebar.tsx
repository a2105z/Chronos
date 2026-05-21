import type { AppView } from "../../types/app";
import "./AppSidebar.css";

const PRIMARY: { id: AppView; label: string; icon: string }[] = [
  { id: "calendar", label: "Planner", icon: "▦" },
  { id: "plan", label: "AI Plan", icon: "✦" },
  { id: "tasks", label: "Priorities", icon: "☰" }
];

const BLOCKING: { id: AppView; label: string }[] = [
  { id: "tasks", label: "Tasks" },
  { id: "availability", label: "Availability" },
  { id: "constraints", label: "Constraints" }
];

interface AppSidebarProps {
  activeView: AppView;
  onSelectView: (view: AppView) => void;
}

export function AppSidebar({ activeView, onSelectView }: AppSidebarProps) {
  return (
    <aside className="sidebar" aria-label="Chronos navigation">
      <div className="sidebar-brand">
        <span className="sidebar-mark">C</span>
        <span className="sidebar-name">Chronos</span>
      </div>

      <nav className="sidebar-nav">
        {PRIMARY.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`sidebar-link ${activeView === item.id ? "active" : ""}`}
            onClick={() => onSelectView(item.id)}
          >
            <span className="sidebar-ico" aria-hidden>
              {item.icon}
            </span>
            {item.label}
          </button>
        ))}

        <p className="sidebar-section">Time blocking</p>
        {BLOCKING.map((item) => (
          <button
            key={`block-${item.id}`}
            type="button"
            className={`sidebar-link sub ${activeView === item.id ? "active" : ""}`}
            onClick={() => onSelectView(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="sidebar-foot">
        <p className="sidebar-foot-line">Constraint-verified scheduling</p>
      </div>
    </aside>
  );
}
