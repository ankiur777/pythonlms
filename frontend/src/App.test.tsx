import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("renders the learning dashboard heading", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Keep building. One line at a time." })).toBeDefined();
  });
});
