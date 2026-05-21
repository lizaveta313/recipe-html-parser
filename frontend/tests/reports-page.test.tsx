import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import ReportsPage from "../app/reports/page";
import { deleteReport, getReports } from "../lib/api";
import { sampleReportListItem } from "./test-data";

vi.mock("../lib/api", () => ({
  getReports: vi.fn(),
  deleteReport: vi.fn()
}));

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  )
}));

describe("ReportsPage", () => {
  beforeEach(() => {
    vi.mocked(getReports).mockReset();
    vi.mocked(deleteReport).mockReset();
    vi.mocked(getReports).mockResolvedValue([sampleReportListItem]);
    vi.mocked(deleteReport).mockResolvedValue();
  });

  test("Reports page отображает список отчетов", async () => {
    render(<ReportsPage />);
    expect(await screen.findByText("Паста с томатами и базиликом")).toBeInTheDocument();
    expect(screen.getByText("manual raw html")).toBeInTheDocument();
    expect(screen.getByText("Полнота")).toBeInTheDocument();
  });
});
