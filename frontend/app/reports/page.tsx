"use client";

import Link from "next/link";
import { Eye, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { deleteReport, getReports } from "../../lib/api";
import type { ReportListItem } from "../../lib/types";
import { ReportSummary } from "../../components/ReportSummary";

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadReports() {
    setLoading(true);
    try {
      setReports(await getReports());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить отчеты");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadReports();
  }, []);

  async function handleDelete(id: string) {
    await deleteReport(id);
    setReports((items) => items.filter((item) => item.id !== id));
  }

  return (
    <main className="page">
      <section className="section-heading">
        <h1>История отчетов</h1>
        <p>Сохраненные результаты анализа HTML-страниц рецептов.</p>
      </section>
      {loading ? <div className="state-box">Загрузка отчетов...</div> : null}
      {error ? <div className="state-box error">{error}</div> : null}
      <div className="reports-list">
        {reports.map((report) => (
          <article className="surface report-row" key={report.id}>
            <div>
              <h2>{report.recipe_title ?? "Название рецепта не найдено"}</h2>
              <p className="muted">{report.source_value}</p>
              <p className="muted">{new Date(report.created_at).toLocaleString("ru-RU")}</p>
              <ReportSummary report={report} />
            </div>
            <div className="row-actions">
              <Link className="icon-button" href={`/reports/${report.id}`} aria-label="Открыть отчет">
                <Eye size={18} />
              </Link>
              <button className="icon-button danger" onClick={() => void handleDelete(report.id)} aria-label="Удалить отчет">
                <Trash2 size={18} />
              </button>
            </div>
          </article>
        ))}
        {!loading && !reports.length ? <div className="state-box">Отчетов пока нет.</div> : null}
      </div>
    </main>
  );
}
