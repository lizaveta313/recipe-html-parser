import type { Ingredient } from "../lib/types";

interface IngredientsListProps {
  ingredients: Ingredient[];
}

export function IngredientsList({ ingredients }: IngredientsListProps) {
  return (
    <section className="surface">
      <h3>Ингредиенты</h3>
      {ingredients.length ? (
        <ul className="ingredient-list">
          {ingredients.map((ingredient) => (
            <li key={ingredient.raw_text}>
              <span>{ingredient.name}</span>
              <strong>{[ingredient.amount, ingredient.unit].filter(Boolean).join(" ") || ingredient.raw_text}</strong>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">Ингредиенты не найдены.</p>
      )}
    </section>
  );
}
