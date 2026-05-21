import { Clock, Star, UserRound, UsersRound } from "lucide-react";
import type { Recipe } from "../lib/types";

interface RecipeCardProps {
  recipe: Recipe;
}

export function RecipeCard({ recipe }: RecipeCardProps) {
  return (
    <section className="surface">
      <div className="recipe-grid">
        {recipe.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img className="recipe-image" src={recipe.image_url} alt={recipe.title ?? "Изображение рецепта"} />
        ) : (
          <div className="recipe-image recipe-image-empty">Нет изображения</div>
        )}
        <div className="recipe-body">
          <div className="kicker">{recipe.source_site}</div>
          <h2>{recipe.title ?? "Название рецепта не найдено"}</h2>
          {recipe.description ? <p className="muted">{recipe.description}</p> : null}
          <div className="meta-row">
            {recipe.author ? (
              <span>
                <UserRound size={16} /> {recipe.author}
              </span>
            ) : null}
            {recipe.cooking_time ? (
              <span>
                <Clock size={16} /> {recipe.cooking_time}
              </span>
            ) : null}
            {recipe.servings ? (
              <span>
                <UsersRound size={16} /> {recipe.servings}
              </span>
            ) : null}
            {recipe.rating ? (
              <span>
                <Star size={16} /> {recipe.rating}
              </span>
            ) : null}
          </div>
          {recipe.tags.length ? (
            <div className="tag-row">
              {recipe.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
