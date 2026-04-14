type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";

interface PrimeNodeProps {
  id: number;
  type: PrimeType;
  mass: number;
  label?: string;
  isPlayer?: boolean;
  onClick?: () => void;
}

const typeColors: Record<PrimeType, { fill: string; glow: string }> = {
  particle: { fill: "#8b5cf6", glow: "rgba(139,92,246,0.3)" },
  force: { fill: "#3b82f6", glow: "rgba(59,130,246,0.3)" },
  field: { fill: "#f59e0b", glow: "rgba(245,158,11,0.3)" },
  law: { fill: "#ef4444", glow: "rgba(239,68,68,0.3)" },
  story: { fill: "#22c55e", glow: "rgba(34,197,94,0.3)" },
  witness: { fill: "#b8b0d0", glow: "rgba(184,176,208,0.2)" },
};

export function PrimeNode({ id, type, mass, label, isPlayer = false, onClick }: PrimeNodeProps) {
  const colors = typeColors[type];
  const radius = Math.max(6, Math.min(20, 6 + mass * 0.5));

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Glow */}
      <circle
        r={radius + 8}
        fill={colors.glow}
        opacity={isPlayer ? 0.6 : 0.3}
      />
      {/* Core */}
      <circle
        r={radius}
        fill={colors.fill}
        stroke={isPlayer ? "#e2e0f0" : "none"}
        strokeWidth={isPlayer ? 1.5 : 0}
      />
      {/* Label */}
      {label && (
        <text
          y={radius + 14}
          textAnchor="middle"
          className="font-ui text-[10px] fill-text-muted"
        >
          {label}
        </text>
      )}
    </g>
  );
}
