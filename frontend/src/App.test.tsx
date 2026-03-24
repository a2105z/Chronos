import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renders Chronos title", () => {
    render(<App />);
    expect(screen.getByText("Chronos")).toBeInTheDocument();
  });

  it("renders Tasks and Calendar tabs", () => {
    render(<App />);
    expect(screen.getByText("Tasks")).toBeInTheDocument();
    expect(screen.getByText("Calendar")).toBeInTheDocument();
  });
});
