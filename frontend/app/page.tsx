import { AnalyzeForm } from "../components/AnalyzeForm";

export default function HomePage() {
  return (
    <main className="page">
      <section className="intro">
        <div>
          <p className="kicker">eda.rambler.ru/recepty</p>
          <h1>Recipe HTML Parser</h1>
          <p>
            Веб-приложение для анализа HTML-страниц рецептов, извлечения данных рецепта,
            поиска ошибок в разметке и сохранения отчетов parser engine.
          </p>
        </div>
      </section>
      <AnalyzeForm />
    </main>
  );
}
