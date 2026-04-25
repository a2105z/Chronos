import type { AppView } from "../../types/app";

interface AppNavProps {
  activeView: AppView;
  onSelectView: (view: AppView) => void;
}

export function AppNav({ activeView, onSelectView }: AppNavProps) {
  function tabClass(view: AppView): string {
    if (activeView === view) {
      return "active";
    }
    return "";
  }

  return (
    <nav className="nav-tabs">
      <button type="button" className={tabClass("tasks")} onClick={() => onSelectView("tasks")}>
        Tasks
      </button>
      <button type="button" className={tabClass("availability")} onClick={() => onSelectView("availability")}>
        Availability
      </button>
      <button type="button" className={tabClass("constraints")} onClick={() => onSelectView("constraints")}>
        Constraints
      </button>
      <button type="button" className={tabClass("calendar")} onClick={() => onSelectView("calendar")}>
        Calendar
      </button>
    </nav>
  );
}
