import { expect, test } from "@playwright/test";

const report = {
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
    image_url: null,
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
    tags: ["паста"],
    equipment: [],
    comments_count: null,
    source_site: "eda.rambler.ru"
  },
  html_analysis: {
    total_tags: 20,
    unique_tags: 10,
    total_links: 1,
    total_images: 0,
    total_text_nodes: 8,
    max_dom_depth: 6,
    html_size_bytes: 1200,
    tokens_count: 60,
    errors_count: 0,
    warnings_count: 0,
    recipe_completeness_score: 95,
    parser_confidence_score: 88
  },
  errors: [],
  warnings: [],
  scores: {
    recipe_completeness_score: 95,
    parser_confidence_score: 88
  },
  dom_tree_preview: { tag: "document", children: [{ tag: "html" }] },
  tokens_preview: [{ type: "OPEN_TAG", value: "html" }]
};

test("raw HTML analysis flow", async ({ page }) => {
  await page.route("**/api/parse/html", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(report) });
  });
  await page.route("**/api/reports", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: report.id,
          source_type: report.source_type,
          source_value: report.source_value,
          recipe_title: report.recipe.title,
          recipe_author: report.recipe.author,
          cooking_time: report.recipe.cooking_time,
          ingredients_count: report.recipe.ingredients.length,
          steps_count: report.recipe.steps.length,
          completeness_score: 95,
          confidence_score: 88,
          errors_count: 0,
          warnings_count: 0,
          created_at: report.created_at
        }
      ])
    });
  });
  await page.route("**/api/reports/report-1", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(report) });
  });

  await page.goto("/");
  await page.getByRole("button", { name: /Raw HTML/i }).click();
  await page.getByLabel("Raw HTML").fill("<html><body><h1>Паста с томатами и базиликом</h1></body></html>");
  await page.getByRole("button", { name: /Analyze/i }).click();

  await expect(page.getByText("Паста с томатами и базиликом").first()).toBeVisible();
  await expect(page.getByText("Спагетти")).toBeVisible();

  await page.getByRole("link", { name: "История" }).click();
  await expect(page.getByText("manual raw html")).toBeVisible();
  await page.getByLabel("Открыть отчет").click();

  await expect(page.getByText("HTML-метрики")).toBeVisible();
  await expect(page.getByText("DOM preview")).toBeVisible();
});
