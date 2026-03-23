/** Top navigation between Tasks and Calendar. */

import type { AppView } from "../../types/app";

interface AppNavProps {
  activeView: AppView;
  onSelectTasks: () => void;
  onSelectCalendar: () => void;
}

export function AppNav({ activeView, onSelectTasks, onSelectCalendar }: AppNavProps) {
  let tasksTabClassName = "";
  if (activeView === "tasks") {
    tasksTabClassName = "active";
  }

  let calendarTabClassName = "";
  if (activeView === "calendar") {
    calendarTabClassName = "active";
  }

  return (
    <nav className="nav-tabs">
      <button type="button" className={tasksTabClassName} onClick={onSelectTasks}>
        Tasks
      </button>
      <button type="button" className={calendarTabClassName} onClick={onSelectCalendar}>
        Calendar
      </button>
    </nav>
  );
}
