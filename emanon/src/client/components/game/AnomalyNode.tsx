type AnomalyType = "merkle_fragment" | "dead_star_remnant" | "high_entropy";

interface AnomalyNodeProps {
  type: AnomalyType;
  label?: string;
  onClick?: () => void;
}

const anomalyConfig: Record<AnomalyType, { stroke: string; glow: string }> = {
  merkle_fragment: { stroke: "#8b5cf6", glow: "rgba(139,92,246,0.15)" },
  dead_star_remnant: { stroke: "#f59e0b", glow: "rgba(245,158,11,0.1)" },
  high_entropy: { stroke: "#ef4444", glow: "rgba(239,68,68,0.1)" },
};

export function AnomalyNode({ type, label, onClick }: AnomalyNodeProps) {
  const config = anomalyConfig[type];

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Pulsing ring */}
      <circle r={14} fill={config.glow} stroke={config.stroke} strokeWidth={1}>
        <animate
          attributeName="r"
          values="12;16;12"
          dur="2s"
          repeatCount="indefinite"
        />
        <animate
          attributeName="opacity"
          values="0.4;1;0.4"
          dur="2s"
          repeatCount="indefinite"
        />
      </circle>
      {/* Label */}
      {label && (
        <text
          y={22}
          textAnchor="middle"
          className="font-ui text-[10px] fill-text-muted"
        >
          {label}
        </text>
      )}
    </g>
  );
}
