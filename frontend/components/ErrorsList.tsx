import { AlertTriangle, Info } from "lucide-react";
import type { ParserIssue } from "../lib/types";

interface ErrorsListProps {
  title: string;
  issues: ParserIssue[];
  kind: "error" | "warning";
}

export function ErrorsList({ title, issues, kind }: ErrorsListProps) {
  const Icon = kind === "error" ? AlertTriangle : Info;
  return (
    <section className="surface">
      <h3>{title}</h3>
      {issues.length ? (
        <ul className="issue-list">
          {issues.map((issue) => (
            <li key={`${issue.code}-${issue.message}`} className={kind}>
              <Icon size={18} />
              <div>
                <strong>{issue.code}</strong>
                <p>{issue.message}</p>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">Ничего не найдено.</p>
      )}
    </section>
  );
}
