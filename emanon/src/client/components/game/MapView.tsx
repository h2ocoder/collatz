"use client";

import { PrimeNode } from "./PrimeNode";
import { StarNode } from "./StarNode";
import { AnomalyNode } from "./AnomalyNode";
import { EnergyBar } from "@/components/ui/EnergyBar";

type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";
type StarState = "healthy" | "dying" | "dead";
type AnomalyType = "merkle_fragment" | "dead_star_remnant" | "high_entropy";

interface MapPrime {
  id: number;
  type: PrimeType;
  mass: number;
  label: string;
  x: number;
  y: number;
  isPlayer?: boolean;
}

interface MapStar {
  id: string;
  luminosity: number;
  state: StarState;
  label: string;
  x: number;
  y: number;
}

interface MapAnomaly {
  id: string;
  type: AnomalyType;
  label: string;
  x: number;
  y: number;
}

interface MapViewProps {
  primes: MapPrime[];
  stars: MapStar[];
  anomalies: MapAnomaly[];
  energy: { current: number; max: number };
  scanRadius?: number;
  playerPosition: { x: number; y: number };
  onPrimeClick?: (id: number) => void;
  onStarClick?: (id: string) => void;
  onAnomalyClick?: (id: string) => void;
}

export function MapView({
  primes,
  stars,
  anomalies,
  energy,
  scanRadius,
  playerPosition,
  onPrimeClick,
  onStarClick,
  onAnomalyClick,
}: MapViewProps) {
  return (
    <div className="relative w-full h-full bg-void overflow-hidden">
      <svg
        className="w-full h-full"
        viewBox="-300 -300 600 600"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Background grid */}
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#1a1520" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect x="-300" y="-300" width="600" height="600" fill="url(#grid)" />

        {/* Scan radius */}
        {scanRadius && (
          <circle
            cx={playerPosition.x}
            cy={playerPosition.y}
            r={scanRadius}
            fill="none"
            stroke="#8b5cf6"
            strokeWidth="0.5"
            strokeDasharray="4 4"
            opacity="0.3"
          />
        )}

        {/* Stars */}
        {stars.map((star) => (
          <g key={star.id} transform={`translate(${star.x}, ${star.y})`}>
            <StarNode
              luminosity={star.luminosity}
              state={star.state}
              label={star.label}
              onClick={() => onStarClick?.(star.id)}
            />
          </g>
        ))}

        {/* Anomalies */}
        {anomalies.map((anomaly) => (
          <g key={anomaly.id} transform={`translate(${anomaly.x}, ${anomaly.y})`}>
            <AnomalyNode
              type={anomaly.type}
              label={anomaly.label}
              onClick={() => onAnomalyClick?.(anomaly.id)}
            />
          </g>
        ))}

        {/* Primes */}
        {primes.map((prime) => (
          <g key={prime.id} transform={`translate(${prime.x}, ${prime.y})`}>
            <PrimeNode
              id={prime.id}
              type={prime.type}
              mass={prime.mass}
              label={prime.label}
              isPlayer={prime.isPlayer}
              onClick={() => onPrimeClick?.(prime.id)}
            />
          </g>
        ))}
      </svg>

      {/* Energy HUD */}
      <div className="absolute bottom-4 left-4 right-4">
        <EnergyBar current={energy.current} max={energy.max} />
      </div>
    </div>
  );
}
