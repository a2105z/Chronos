import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import App from "../src/App";
import { AuthProvider } from "../src/auth/AuthContext";

vi.mock("../src/components/calendar/CalendarView", () => ({
  default: () => <div data-testid="planner-stub">Planner stub</div>
}));

vi.mock("../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../src/api/client")>("../src/api/client");
  return {
    ...actual,
    getMe: vi.fn().mockResolvedValue({
      data: { id: 1, email: "demo@chronos.app", name: "Demo", created_at: "2030-01-01T00:00:00" }
    }),
    getTasks: vi.fn().mockResolvedValue({ data: [] }),
    getSuggestions: vi.fn().mockResolvedValue({ data: { suggestions: ["Add availability"] } }),
    getStoredToken: vi.fn().mockReturnValue("test-token"),
    setStoredToken: vi.fn()
  };
});

describe("App", () => {
  beforeEach(() => {
    localStorage.setItem("chronos_token", "test-token");
  });

  it("renders Reclaim-style shell with Planner navigation", async () => {
    render(
      <MemoryRouter initialEntries={["/app"]}>
        <AuthProvider>
          <Routes>
            <Route path="/app/*" element={<App />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByRole("button", { name: "Planner" })).toBeInTheDocument();
    expect(screen.getAllByText("Chronos").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "AI Plan" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Plan with AI/i })).toBeInTheDocument();
    expect(screen.getByTestId("planner-stub")).toBeInTheDocument();
  });
});
