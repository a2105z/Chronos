import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../src/App";

describe("App", () => {
  it("renders the shell with title and navigation", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Chronos" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tasks" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Availability" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Constraints" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Calendar" })).toBeInTheDocument();
  });
});
