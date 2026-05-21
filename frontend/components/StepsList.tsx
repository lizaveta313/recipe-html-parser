import type { RecipeStep } from "../lib/types";

interface StepsListProps {
  steps: RecipeStep[];
}

export function StepsList({ steps }: StepsListProps) {
  return (
    <section className="surface">
      <h3>Шаги приготовления</h3>
      {steps.length ? (
        <ol className="steps-list">
          {steps.map((step) => (
            <li key={`${step.step_number}-${step.text}`}>
              <span>{step.step_number}</span>
              <p>{step.text}</p>
            </li>
          ))}
        </ol>
      ) : (
        <p className="muted">Шаги приготовления не найдены.</p>
      )}
    </section>
  );
}
