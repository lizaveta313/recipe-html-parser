"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { DomTreePreview } from "../../../components/DomTreePreview";
import { ErrorsList } from "../../../components/ErrorsList";
import { HtmlMetricsTable } from "../../../components/HtmlMetricsTable";
import { IngredientsList } from "../../../components/IngredientsList";
import { NutritionTable } from "../../../components/NutritionTable";
import { RecipeCard } from "../../../components/RecipeCard";
import { ReportSummary } from "../../../components/ReportSummary";
import { StepsList } from "../../../components/StepsList";
import { getReport } from "../../../lib/api";
import type { ParserReport } from "../../../lib/types";

export default function ReportDetailsPage() {
  const params = useParams<{ id: string }>();
  const [report, setReport] = useState<ParserReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    getReport(params.id)
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Не удалось загрузить отчет"));
  }, [params.id]);

  if (error) {
    return <main className="page"><div className="state-box error">{error}</div></main>;
  }

  if (!report) {
    return <main className="page"><div className="state-box">Загрузка отчета...</div></main>;
  }

  return (
    <main className="page">
      <section className="section-heading">
        <h1>{report.recipe.title ?? "Отчет по рецепту"}</h1>
        <p>{report.source_value}</p>
      </section>
      <ReportSummary report={report} />
      <RecipeCard recipe={report.recipe} />
      <div className="two-column">
        <IngredientsList ingredients={report.recipe.ingredients} />
        <NutritionTable nutrition={report.recipe.nutrition} />
      </div>
      <StepsList steps={report.recipe.steps} />
      <div className="two-column">
        <ErrorsList title="Ошибки" issues={report.errors} kind="error" />
        <ErrorsList title="Предупреждения" issues={report.warnings} kind="warning" />
      </div>
      <HtmlMetricsTable metrics={report.html_analysis} />
      <DomTreePreview tree={report.dom_tree_preview} tokens={report.tokens_preview} />
    </main>
  );
}
