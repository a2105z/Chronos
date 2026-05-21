import { useState } from "react";
import type { FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import "./AuthScreen.css";

export default function AuthScreen() {
  const { user, loading, login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@chronos.app");
  const [password, setPassword] = useState("chronos-demo");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (!loading && user) {
    return <Navigate to="/app" replace />;
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password, name || email.split("@")[0]);
      }
      navigate("/app");
    } catch {
      setError(mode === "login" ? "Login failed. Check email and password." : "Registration failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-atmosphere" aria-hidden="true" />
      <div className="auth-panel">
        <p className="brand-mark">Chronos</p>
        <p className="auth-sub">
          Tell it your week in plain English. A verified engine places the blocks.
        </p>

        <form className="auth-form" onSubmit={onSubmit}>
          {mode === "register" ? (
            <label>
              Name
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
            </label>
          ) : null}
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
          </label>
          {error ? <p className="auth-error">{error}</p> : null}
          <button type="submit" className="btn-primary auth-submit" disabled={busy}>
            {busy ? "Working…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <button
          type="button"
          className="auth-switch"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Need an account? Register" : "Have an account? Sign in"}
        </button>
        <p className="auth-demo">Demo: demo@chronos.app / chronos-demo</p>
      </div>
    </div>
  );
}
