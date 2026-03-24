/** Chronos - main app with tasks and calendar views. */

import { useState } from "react";
import TaskList from "./components/TaskList";
import CalendarView from "./components/CalendarView";
import "./App.css";


function App() {
  const [activeView, setActiveView] = useState<"tasks" | "calendar">("tasks");

  let tasksTabClass = "";
  if (activeView === "tasks") {
    tasksTabClass = "active";
  }

  let calendarTabClass = "";
  if (activeView === "calendar") {
    calendarTabClass = "active";
  }

  function handleTasksClick() {
    setActiveView("tasks");
  }

  function handleCalendarClick() {
    setActiveView("calendar");
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Chronos</h1>
        <p className="tagline">Intelligent Constraint-Aware Time Blocking</p>
        <nav className="nav-tabs">
          <button className={tasksTabClass} onClick={handleTasksClick}>
            Tasks
          </button>
          <button className={calendarTabClass} onClick={handleCalendarClick}>
            Calendar
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeView === "tasks" && <TaskList />}
        {activeView === "calendar" && <CalendarView />}
      </main>
    </div>
  );
}

export default App;
