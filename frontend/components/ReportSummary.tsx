import { Gauge, TriangleAlert } from "lucide-react";
import type { ParserReport, ReportListItem } from "../lib/types";

type ReportLike = ParserReport | ReportListItem;

function getValue(report: ReportLike, field: "completeness" | "confidence" | "errors") {
  if ("scores" in report) {
    if (field === "completeness") return report.scores.recipe_completeness_score;
    if (field === "confidence") return report.scores.parser_confidence_score;
    return report.errors.length;
  }
  if (field === "completeness") return report.completeness_score;
  if (field === "confidence") return report.confidence_score;
  return report.errors_count;
}

export function ReportSummary({ report }: { report: ReportLike }) {
  return (
    <section className="summary-grid" aria-label="Краткая сводка отчета">
      <div className="summary-item">
        <Gauge size={18} />
        <span>Полнота</span>
        <strong>{getValue(report, "completeness")}%</strong>
      </div>
      <div className="summary-item">
        <Gauge size={18} />
        <span>Уверенность</span>
        <strong>{getValue(report, "confidence")}%</strong>
      </div>
      <div className="summary-item">
        <TriangleAlert size={18} />
        <span>Ошибки</span>
        <strong>{getValue(report, "errors")}</strong>
      </div>
    </section>
  );
}
