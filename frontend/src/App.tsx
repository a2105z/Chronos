import { useState } from "react";
import type { ReactNode } from "react";
import type { AppView } from "./types/app";
import { AppHeader } from "./components/layout/AppHeader";
import TaskList from "./components/tasks/TaskList";
import CalendarView from "./components/calendar/CalendarView";
import AvailabilityView from "./components/availability/AvailabilityView";
import ConstraintsView from "./components/constraints/ConstraintsView";
import { getStartOfWeekMonday } from "./utils/calendarGrid";
import "./App.css";

export default function App() {
  const [activeView, setActiveView] = useState<AppView>("tasks");
  const [calendarRefreshTrigger, setCalendarRefreshTrigger] = useState(0);
  const [weekMonday, setWeekMonday] = useState(() => getStartOfWeekMonday());

  function handleSelectView(view: AppView) {
    if (view === "calendar" && activeView !== "calendar") {
      setWeekMonday(getStartOfWeekMonday());
    }
    setActiveView(view);
  }

  function handleTaskCreated() {
    setCalendarRefreshTrigger(function bumpCounter(previousValue) {
      return previousValue + 1;
    });
  }

  let mainContent: ReactNode = null;
  if (activeView === "tasks") {
    mainContent = <TaskList onTaskCreated={handleTaskCreated} />;
  }
  if (activeView === "availability") {
    mainContent = <AvailabilityView />;
  }
  if (activeView === "constraints") {
    mainContent = <ConstraintsView />;
  }
  if (activeView === "calendar") {
    mainContent = (
      <CalendarView
        refreshTrigger={calendarRefreshTrigger}
        weekMonday={weekMonday}
        onWeekChange={setWeekMonday}
      />
    );
  }

  return (
    <div className="app">
      <AppHeader activeView={activeView} onSelectView={handleSelectView} />
      <main className="app-main">{mainContent}</main>
    </div>
  );
}
