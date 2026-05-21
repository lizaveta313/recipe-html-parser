import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import { ErrorsList } from "../components/ErrorsList";
import { IngredientsList } from "../components/IngredientsList";
import { RecipeCard } from "../components/RecipeCard";
import { StepsList } from "../components/StepsList";
import { sampleReport } from "./test-data";

describe("recipe components", () => {
  test("RecipeCard отображает название, время и автора", () => {
    render(<RecipeCard recipe={sampleReport.recipe} />);
    expect(screen.getByText("Паста с томатами и базиликом")).toBeInTheDocument();
    expect(screen.getByText("35 мин")).toBeInTheDocument();
    expect(screen.getByText("Редакция Еда")).toBeInTheDocument();
  });

  test("IngredientsList отображает список ингредиентов", () => {
    render(<IngredientsList ingredients={sampleReport.recipe.ingredients} />);
    expect(screen.getByText("Спагетти")).toBeInTheDocument();
    expect(screen.getByText("400 г")).toBeInTheDocument();
  });

  test("StepsList отображает шаги", () => {
    render(<StepsList steps={sampleReport.recipe.steps} />);
    expect(screen.getByText("Отварите спагетти в подсоленной воде.")).toBeInTheDocument();
  });

  test("ErrorsList отображает ошибки", () => {
    render(
      <ErrorsList
        title="Ошибки"
        kind="error"
        issues={[{ severity: "error", code: "MISSING_TITLE", message: "Title missing." }]}
      />
    );
    expect(screen.getByText("MISSING_TITLE")).toBeInTheDocument();
    expect(screen.getByText("Title missing.")).toBeInTheDocument();
  });
});
