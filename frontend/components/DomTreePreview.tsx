interface DomTreePreviewProps {
  tree: Record<string, unknown>;
  tokens: Array<Record<string, unknown>>;
}

export function DomTreePreview({ tree, tokens }: DomTreePreviewProps) {
  return (
    <section className="surface preview-grid">
      <div>
        <h3>DOM preview</h3>
        <pre>{JSON.stringify(tree, null, 2)}</pre>
      </div>
      <div>
        <h3>Tokens preview</h3>
        <pre>{JSON.stringify(tokens, null, 2)}</pre>
      </div>
    </section>
  );
}

