/** Chronos - main shell with Tasks and Calendar views. */

import { useState } from "react";
import type { ReactNode } from "react";
import type { AppView } from "./types/app";
import { AppHeader } from "./components/layout/AppHeader";
import TaskList from "./components/tasks/TaskList";
import CalendarView from "./components/calendar/CalendarView";
import "./App.css";

function App() {
  const [activeView, setActiveView] = useState<AppView>("tasks");
  const [calendarRefreshTrigger, setCalendarRefreshTrigger] = useState(0);

  function handleSelectTasks() {
    setActiveView("tasks");
  }

  function handleSelectCalendar() {
    setActiveView("calendar");
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
  if (activeView === "calendar") {
    mainContent = <CalendarView refreshTrigger={calendarRefreshTrigger} />;
  }

  return (
    <div className="app">
      <AppHeader
        activeView={activeView}
        onSelectTasks={handleSelectTasks}
        onSelectCalendar={handleSelectCalendar}
      />
      <main className="app-main">{mainContent}</main>
    </div>
  );
}

export default App;
