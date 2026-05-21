import { useAuth } from "../../auth/AuthContext";
import "./AppTopBar.css";

interface AppTopBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  onOpenPlan: () => void;
}

export function AppTopBar({ search, onSearchChange, onOpenPlan }: AppTopBarProps) {
  const { user, logout } = useAuth();
  const initials = (user?.name || user?.email || "C")
    .split(/\s+/)
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="topbar">
      <label className="topbar-search">
        <span className="topbar-search-ico" aria-hidden>
          ⌕
        </span>
        <input
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Find tasks or times"
          aria-label="Search tasks"
        />
      </label>

      <div className="topbar-actions">
        <button type="button" className="topbar-ghost" onClick={onOpenPlan}>
          + Plan with AI
        </button>
        <div className="topbar-avatar" title={user?.email}>
          {initials}
        </div>
        <button type="button" className="topbar-ghost quiet" onClick={logout}>
          Log out
        </button>
      </div>
    </header>
  );
}
