import type { AppView } from "../../types/app";
import { AppNav } from "./AppNav";
import { useAuth } from "../../auth/AuthContext";

interface AppHeaderProps {
  activeView: AppView;
  onSelectView: (view: AppView) => void;
}

export function AppHeader({ activeView, onSelectView }: AppHeaderProps) {
  const { user, logout } = useAuth();

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <div className="header-top">
          <div>
            <p className="brand-inline">Chronos</p>
            <p className="tagline">Intent in · verified blocks out</p>
          </div>
          <div className="header-user">
            <span className="user-chip">{user?.name || user?.email}</span>
            <button type="button" className="btn-secondary" onClick={logout}>
              Log out
            </button>
          </div>
        </div>
        <AppNav activeView={activeView} onSelectView={onSelectView} />
      </div>
    </header>
  );
}
