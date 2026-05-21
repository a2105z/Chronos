import type { AppView } from "../../types/app";

const TABS: { id: AppView; label: string }[] = [
  { id: "plan", label: "Plan" },
  { id: "calendar", label: "Calendar" },
  { id: "tasks", label: "Tasks" },
  { id: "availability", label: "Availability" },
  { id: "constraints", label: "Constraints" }
];

interface AppNavProps {
  activeView: AppView;
  onSelectView: (view: AppView) => void;
}

export function AppNav({ activeView, onSelectView }: AppNavProps) {
  return (
    <nav className="nav-tabs" aria-label="Primary">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={activeView === tab.id ? "active" : ""}
          onClick={() => onSelectView(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
