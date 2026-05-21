import type { ParserReport, ReportListItem } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (typeof body.error?.message === "string") {
        message = body.error.message;
      }
    } catch {
      // Keep default message.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function parseUrl(url: string): Promise<ParserReport> {
  return request<ParserReport>("/api/parse/url", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function parseHtml(html: string, sourceName = "manual test"): Promise<ParserReport> {
  return request<ParserReport>("/api/parse/html", {
    method: "POST",
    body: JSON.stringify({ html, source_name: sourceName }),
  });
}

export function getReports(): Promise<ReportListItem[]> {
  return request<ReportListItem[]>("/api/reports");
}

export function getReport(id: string): Promise<ParserReport> {
  return request<ParserReport>(`/api/reports/${id}`);
}

export async function deleteReport(id: string): Promise<void> {
  await request<{ deleted: boolean }>(`/api/reports/${id}`, { method: "DELETE" });
}
