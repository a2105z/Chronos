/** App title, tagline, and primary navigation. */

import type { AppView } from "../../types/app";
import { AppNav } from "./AppNav";

interface AppHeaderProps {
  activeView: AppView;
  onSelectTasks: () => void;
  onSelectCalendar: () => void;
}

export function AppHeader({ activeView, onSelectTasks, onSelectCalendar }: AppHeaderProps) {
  return (
    <header className="app-header">
      <h1>Chronos</h1>
      <p className="tagline">Intelligent Constraint-Aware Time Blocking</p>
      <AppNav
        activeView={activeView}
        onSelectTasks={onSelectTasks}
        onSelectCalendar={onSelectCalendar}
      />
    </header>
  );
}
