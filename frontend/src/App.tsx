import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import type { AppView } from "./types/app";
import { useAuth } from "./auth/AuthContext";
import { AppSidebar } from "./components/layout/AppSidebar";
import { AppTopBar } from "./components/layout/AppTopBar";
import { RightRail } from "./components/layout/RightRail";
import PlanView from "./components/plan/PlanView";
import TaskList from "./components/tasks/TaskList";
import CalendarView from "./components/calendar/CalendarView";
import AvailabilityView from "./components/availability/AvailabilityView";
import ConstraintsView from "./components/constraints/ConstraintsView";
import { getStartOfWeekMonday } from "./utils/calendarGrid";
import { getTasks } from "./api/client";
import type { Task } from "./types/task";
import type { UnscheduledDiagnostic } from "./types/schedule";
import "./App.css";

export default function App() {
  const { user, loading } = useAuth();
  const [activeView, setActiveView] = useState<AppView>("calendar");
  const [calendarRefreshTrigger, setCalendarRefreshTrigger] = useState(0);
  const [weekMonday, setWeekMonday] = useState(() => getStartOfWeekMonday());
  const [tasks, setTasks] = useState<Task[]>([]);
  const [unscheduled, setUnscheduled] = useState<UnscheduledDiagnostic[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!user) {
      return;
    }
    getTasks()
      .then((res) => setTasks(res.data))
      .catch(() => setTasks([]));
  }, [user, calendarRefreshTrigger, activeView]);

  const filteredTasks = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) {
      return tasks;
    }
    return tasks.filter((t) => t.name.toLowerCase().includes(q));
  }, [tasks, search]);

  if (loading) {
    return <div className="boot-screen">Loading Chronos…</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  function bumpCalendar() {
    setCalendarRefreshTrigger((n) => n + 1);
  }

  function handleSelectView(view: AppView) {
    if (view === "calendar") {
      setWeekMonday(getStartOfWeekMonday());
    }
    setActiveView(view);
  }

  function handlePlanned() {
    bumpCalendar();
    setActiveView("calendar");
  }

  function handleTaskCreated() {
    bumpCalendar();
  }

  let center: ReactNode = null;
  if (activeView === "calendar") {
    center = (
      <CalendarView
        refreshTrigger={calendarRefreshTrigger}
        weekMonday={weekMonday}
        onWeekChange={setWeekMonday}
        onUnscheduledChange={setUnscheduled}
        embed
      />
    );
  } else if (activeView === "plan") {
    center = <PlanView onPlanned={handlePlanned} />;
  } else if (activeView === "tasks") {
    center = <TaskList onTaskCreated={handleTaskCreated} />;
  } else if (activeView === "availability") {
    center = <AvailabilityView />;
  } else if (activeView === "constraints") {
    center = <ConstraintsView />;
  }

  return (
    <div className="shell">
      <AppSidebar activeView={activeView} onSelectView={handleSelectView} />
      <div className="shell-main">
        <AppTopBar
          search={search}
          onSearchChange={setSearch}
          onOpenPlan={() => setActiveView("plan")}
        />
        <div className="shell-body">
          <div className="shell-center">{center}</div>
          <RightRail
            tasks={filteredTasks}
            unscheduled={unscheduled}
            search={search}
            onSearchChange={setSearch}
            onGoPlanner={() => handleSelectView("calendar")}
          />
        </div>
      </div>
    </div>
  );
}
