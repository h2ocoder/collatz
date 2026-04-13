type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";

interface BadgeProps {
  type: PrimeType;
  className?: string;
}

const typeStyles: Record<PrimeType, { border: string; text: string }> = {
  particle: { border: "border-accent-violet/40", text: "text-accent-violet" },
  force: { border: "border-accent-blue/40", text: "text-accent-blue" },
  field: { border: "border-star/40", text: "text-star" },
  law: { border: "border-danger/40", text: "text-danger" },
  story: { border: "border-trust/40", text: "text-trust" },
  witness: { border: "border-text-muted/40", text: "text-text-secondary" },
};

export function Badge({ type, className = "" }: BadgeProps) {
  const styles = typeStyles[type];
  return (
    <span className={`font-data text-xs border px-2 py-0.5 rounded-sm ${styles.border} ${styles.text} ${className}`}>
      {type}
    </span>
  );
}
