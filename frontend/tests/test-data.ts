import type { ParserReport, ReportListItem } from "../lib/types";

export const sampleReport: ParserReport = {
  id: "report-1",
  source_type: "raw_html",
  source_value: "manual raw html",
  created_at: "2026-05-11T12:00:00Z",
  recipe: {
    title: "Паста с томатами и базиликом",
    original_url: null,
    author: "Редакция Еда",
    category: "Паста",
    servings: "4 порции",
    cooking_time: "35 мин",
    image_url: "https://eda.rambler.ru/images/recipe/pasta.jpg",
    rating: "4.8",
    description: "Простая паста с насыщенным томатным соусом.",
    ingredients: [
      { name: "Спагетти", amount: "400", unit: "г", raw_text: "Спагетти 400 г" },
      { name: "Помидоры", amount: "500", unit: "г", raw_text: "Помидоры 500 г" }
    ],
    steps: [
      { step_number: 1, text: "Отварите спагетти в подсоленной воде." },
      { step_number: 2, text: "Смешайте пасту с томатным соусом." }
    ],
    nutrition: { calories: 420, proteins: 12, fats: 14, carbohydrates: 64 },
    tags: ["паста", "ужин"],
    equipment: ["кастрюля"],
    comments_count: 12,
    source_site: "eda.rambler.ru"
  },
  html_analysis: {
    total_tags: 120,
    unique_tags: 25,
    total_links: 20,
    total_images: 5,
    total_text_nodes: 40,
    max_dom_depth: 12,
    html_size_bytes: 50000,
    tokens_count: 350,
    errors_count: 0,
    warnings_count: 1,
    recipe_completeness_score: 100,
    parser_confidence_score: 90
  },
  errors: [],
  warnings: [{ severity: "warning", code: "MISSING_CATEGORY", message: "Category missing." }],
  scores: {
    recipe_completeness_score: 100,
    parser_confidence_score: 90
  },
  dom_tree_preview: { tag: "document", children: [{ tag: "html" }] },
  tokens_preview: [{ type: "OPEN_TAG", value: "html" }]
};

export const sampleReportListItem: ReportListItem = {
  id: sampleReport.id,
  source_type: "raw_html",
  source_value: sampleReport.source_value,
  recipe_title: sampleReport.recipe.title,
  recipe_author: sampleReport.recipe.author,
  cooking_time: sampleReport.recipe.cooking_time,
  ingredients_count: sampleReport.recipe.ingredients.length,
  steps_count: sampleReport.recipe.steps.length,
  completeness_score: 100,
  confidence_score: 90,
  errors_count: 0,
  warnings_count: 1,
  created_at: sampleReport.created_at
};
