import type { Nutrition } from "../lib/types";

interface NutritionTableProps {
  nutrition?: Nutrition | null;
}

export function NutritionTable({ nutrition }: NutritionTableProps) {
  const rows: Array<[string, number | null | undefined, string]> = [
    ["Калории", nutrition?.calories, "ккал"],
    ["Белки", nutrition?.proteins, "г"],
    ["Жиры", nutrition?.fats, "г"],
    ["Углеводы", nutrition?.carbohydrates, "г"],
  ];

  return (
    <section className="surface">
      <h3>Пищевая ценность</h3>
      <table className="metrics-table">
        <tbody>
          {rows.map(([label, value, unit]) => (
            <tr key={label}>
              <th>{label}</th>
              <td>{value ?? "не найдено"} {value ? unit : ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
