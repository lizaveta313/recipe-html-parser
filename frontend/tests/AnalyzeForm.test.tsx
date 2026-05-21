import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { AnalyzeForm } from "../components/AnalyzeForm";
import { parseHtml, parseUrl } from "../lib/api";
import { sampleReport } from "./test-data";

vi.mock("../lib/api", () => ({
  parseHtml: vi.fn(),
  parseUrl: vi.fn()
}));

describe("AnalyzeForm", () => {
  beforeEach(() => {
    vi.mocked(parseHtml).mockReset();
    vi.mocked(parseUrl).mockReset();
    vi.mocked(parseHtml).mockResolvedValue(sampleReport);
    vi.mocked(parseUrl).mockResolvedValue(sampleReport);
  });

  test("переключает режим URL / Raw HTML", async () => {
    const user = userEvent.setup();
    render(<AnalyzeForm />);

    expect(screen.getByLabelText("Recipe URL")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Raw HTML/i }));
    expect(screen.getByLabelText("Raw HTML")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /^URL$/i }));
    expect(screen.getByLabelText("Recipe URL")).toBeInTheDocument();
  });

  test("форма отправляет URL", async () => {
    const user = userEvent.setup();
    render(<AnalyzeForm />);

    await user.type(screen.getByLabelText("Recipe URL"), "https://eda.rambler.ru/recepty/pasta/example");
    await user.click(screen.getByRole("button", { name: /Analyze/i }));

    await waitFor(() => expect(parseUrl).toHaveBeenCalledWith("https://eda.rambler.ru/recepty/pasta/example"));
    expect(await screen.findByText("Паста с томатами и базиликом")).toBeInTheDocument();
  });

  test("форма отправляет raw HTML", async () => {
    const user = userEvent.setup();
    render(<AnalyzeForm />);

    await user.click(screen.getByRole("button", { name: /Raw HTML/i }));
    await user.type(screen.getByLabelText("Raw HTML"), "<html><body><h1>Recipe</h1></body></html>");
    await user.click(screen.getByRole("button", { name: /Analyze/i }));

    await waitFor(() =>
      expect(parseHtml).toHaveBeenCalledWith("<html><body><h1>Recipe</h1></body></html>", "manual raw html")
    );
  });
});
