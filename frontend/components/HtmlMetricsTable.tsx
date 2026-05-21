import type { HtmlMetrics } from "../lib/types";

interface HtmlMetricsTableProps {
  metrics: HtmlMetrics;
}

export function HtmlMetricsTable({ metrics }: HtmlMetricsTableProps) {
  const rows: Array<[string, number | string]> = [
    ["Токены", metrics.tokens_count],
    ["Теги", metrics.total_tags],
    ["Уникальные теги", metrics.unique_tags],
    ["Ссылки", metrics.total_links],
    ["Изображения", metrics.total_images],
    ["Текстовые узлы", metrics.total_text_nodes],
    ["Максимальная глубина DOM", metrics.max_dom_depth],
    ["Размер HTML", `${metrics.html_size_bytes} bytes`],
  ];

  return (
    <section className="surface">
      <h3>HTML-метрики</h3>
      <table className="metrics-table">
        <tbody>
          {rows.map(([label, value]) => (
            <tr key={label}>
              <th>{label}</th>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
