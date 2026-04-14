"use client";

interface EnergyBarProps {
  current: number;
  max: number;
  className?: string;
}

function getEnergyState(current: number, max: number) {
  const ratio = current / max;
  if (ratio > 0.5) return { gradient: "from-star to-amber-300", label: "text-star" };
  if (ratio > 0.2) return { gradient: "from-orange-500 to-star", label: "text-orange-400" };
  return { gradient: "from-danger to-red-400", label: "text-danger" };
}

export function EnergyBar({ current, max, className = "" }: EnergyBarProps) {
  const pct = Math.max(0, Math.min(100, (current / max) * 100));
  const state = getEnergyState(current, max);

  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-1">
        <span className="font-ui text-xs text-text-secondary">Energy</span>
        <span className={`font-data text-xs ${state.label}`}>{current} / {max}</span>
      </div>
      <div className="h-1.5 bg-raised rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${state.gradient} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
