type StarState = "healthy" | "dying" | "dead";

interface StarNodeProps {
  luminosity: number;
  state: StarState;
  label?: string;
  onClick?: () => void;
}

const stateConfig: Record<StarState, { fill: string; glow: string; pulseSpeed: string }> = {
  healthy: { fill: "#f59e0b", glow: "rgba(245,158,11,0.4)", pulseSpeed: "3s" },
  dying: { fill: "#d97706", glow: "rgba(217,119,6,0.2)", pulseSpeed: "5s" },
  dead: { fill: "#6b6880", glow: "rgba(107,104,128,0.1)", pulseSpeed: "0s" },
};

export function StarNode({ luminosity, state, label, onClick }: StarNodeProps) {
  const config = stateConfig[state];
  const radius = Math.max(10, Math.min(24, 10 + luminosity * 2));

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Outer glow */}
      {state !== "dead" && (
        <circle r={radius + 16} fill={config.glow}>
          <animate
            attributeName="r"
            values={`${radius + 12};${radius + 20};${radius + 12}`}
            dur={config.pulseSpeed}
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.3;0.6;0.3"
            dur={config.pulseSpeed}
            repeatCount="indefinite"
          />
        </circle>
      )}
      {/* Core */}
      <circle r={radius} fill={config.fill} />
      {/* Label */}
      {label && (
        <text
          y={radius + 16}
          textAnchor="middle"
          className="font-ui text-[10px] fill-text-muted"
        >
          {label}
        </text>
      )}
    </g>
  );
}
