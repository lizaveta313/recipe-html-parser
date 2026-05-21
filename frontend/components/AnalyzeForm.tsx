"use client";

import { FormEvent, useState } from "react";
import { FileText, Link as LinkIcon, Loader2, Play } from "lucide-react";
import { parseHtml, parseUrl } from "../lib/api";
import type { ParserReport } from "../lib/types";
import { IngredientsList } from "./IngredientsList";
import { RecipeCard } from "./RecipeCard";
import { ReportSummary } from "./ReportSummary";

type Mode = "url" | "html";

export function AnalyzeForm() {
  const [mode, setMode] = useState<Mode>("url");
  const [url, setUrl] = useState("");
  const [html, setHtml] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ParserReport | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = mode === "url" ? await parseUrl(url) : await parseHtml(html, "manual raw html");
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось выполнить анализ");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <form className="surface form-surface" onSubmit={handleSubmit}>
        <div className="mode-switch" role="tablist" aria-label="Режим анализа">
          <button
            type="button"
            className={mode === "url" ? "active" : ""}
            onClick={() => setMode("url")}
            aria-pressed={mode === "url"}
          >
            <LinkIcon size={17} /> URL
          </button>
          <button
            type="button"
            className={mode === "html" ? "active" : ""}
            onClick={() => setMode("html")}
            aria-pressed={mode === "html"}
          >
            <FileText size={17} /> Raw HTML
          </button>
        </div>

        {mode === "url" ? (
          <label className="field">
            <span>URL eda.rambler.ru/recepty</span>
            <input
              aria-label="Recipe URL"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://eda.rambler.ru/recepty/..."
            />
          </label>
        ) : (
          <label className="field">
            <span>HTML-код</span>
            <textarea
              aria-label="Raw HTML"
              value={html}
              onChange={(event) => setHtml(event.target.value)}
              placeholder="<html>...</html>"
              rows={10}
            />
          </label>
        )}

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? <Loader2 className="spin" size={18} /> : <Play size={18} />}
          Analyze
        </button>
      </form>

      {loading ? <div className="state-box">Parser engine выполняет анализ...</div> : null}
      {error ? <div className="state-box error">Ошибка: {error}</div> : null}
      {report ? (
        <div className="stack">
          <ReportSummary report={report} />
          <RecipeCard recipe={report.recipe} />
          <IngredientsList ingredients={report.recipe.ingredients} />
        </div>
      ) : null}
    </div>
  );
}
