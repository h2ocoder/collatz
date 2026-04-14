"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { PrimeNode } from "./PrimeNode";
import { StarNode } from "./StarNode";
import { AnomalyNode } from "./AnomalyNode";
import { EnergyBar } from "@/components/ui/EnergyBar";

type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";
type StarState = "healthy" | "dying" | "dead";
type AnomalyType = "merkle_fragment" | "dead_star_remnant" | "high_entropy";

// Hex size must match the pattern: flat-top hex with center-to-vertex = 25
const HEX_SIZE = 25;
const SQRT3 = Math.sqrt(3);

// Axial coord → world position for flat-top hex
function hexToWorld(q: number, r: number): [number, number] {
  return [1.5 * HEX_SIZE * q, SQRT3 * HEX_SIZE * (r + q / 2)];
}

// Flat-top hex vertex offset for vertex index 0–5
function hexVertex(i: number): [number, number] {
  const angle = (Math.PI / 3) * i;
  return [HEX_SIZE * Math.cos(angle), HEX_SIZE * Math.sin(angle)];
}

// Edge i → axial neighbor offset (flat-top)
const NEIGHBOR_OFFSETS: [number, number][] = [
  [1, 0], [0, 1], [-1, 1], [-1, 0], [0, -1], [1, -1],
];

/**
 * Compute SVG path for the boundary of all hex cells whose centers
 * fall within `radius` of (`px`, `py`). The boundary follows cell edges.
 */
function hexBoundaryPath(px: number, py: number, radius: number): string {
  const searchQ = Math.ceil(radius / (1.5 * HEX_SIZE)) + 1;
  const searchR = Math.ceil(radius / (SQRT3 * HEX_SIZE)) + 1;
  const key = (q: number, r: number) => `${q},${r}`;

  // Find all cells inside the radius
  const inside = new Set<string>();
  for (let q = -searchQ; q <= searchQ; q++) {
    for (let r = -searchR; r <= searchR; r++) {
      const [wx, wy] = hexToWorld(q, r);
      const dx = wx - px;
      const dy = wy - py;
      if (dx * dx + dy * dy <= radius * radius) {
        inside.add(key(q, r));
      }
    }
  }

  // Collect boundary edges: edges of inside cells with an outside neighbor
  const segments: string[] = [];
  for (const cellKey of inside) {
    const [q, r] = cellKey.split(",").map(Number);
    const [cx, cy] = hexToWorld(q, r);
    for (let i = 0; i < 6; i++) {
      const [dq, dr] = NEIGHBOR_OFFSETS[i];
      if (!inside.has(key(q + dq, r + dr))) {
        const [vx1, vy1] = hexVertex(i);
        const [vx2, vy2] = hexVertex((i + 1) % 6);
        segments.push(
          `M${cx + vx1},${cy + vy1}L${cx + vx2},${cy + vy2}`
        );
      }
    }
  }

  return segments.join("");
}

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
  const scanPath = useMemo(
    () => scanRadius
      ? hexBoundaryPath(playerPosition.x, playerPosition.y, scanRadius)
      : null,
    [playerPosition.x, playerPosition.y, scanRadius]
  );

  // --- Pan & zoom state ---
  const svgRef = useRef<SVGSVGElement>(null);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const dragging = useRef<{ startX: number; startY: number; panX: number; panY: number } | null>(null);

  const MIN_ZOOM = 0.3;
  const MAX_ZOOM = 4;
  const VIEW_SIZE = 600;
  const HALF = VIEW_SIZE / 2;

  // Mouse/touch → SVG coordinate scale factor
  const clientToSvg = useCallback((clientDx: number, clientDy: number): [number, number] => {
    if (!svgRef.current) return [clientDx, clientDy];
    const rect = svgRef.current.getBoundingClientRect();
    const scale = VIEW_SIZE / Math.min(rect.width, rect.height);
    return [clientDx * scale, clientDy * scale];
  }, []);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    if (e.button !== 0) return;
    (e.target as Element).setPointerCapture(e.pointerId);
    dragging.current = { startX: e.clientX, startY: e.clientY, panX: pan.x, panY: pan.y };
  }, [pan]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!dragging.current) return;
    const [dx, dy] = clientToSvg(
      e.clientX - dragging.current.startX,
      e.clientY - dragging.current.startY,
    );
    setPan({
      x: dragging.current.panX + dx / zoom,
      y: dragging.current.panY + dy / zoom,
    });
  }, [zoom, clientToSvg]);

  const handlePointerUp = useCallback(() => {
    dragging.current = null;
  }, []);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom((z) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z * factor)));
  }, []);

  // Background rect big enough to cover viewport at any zoom/pan
  const bgExtent = HALF / Math.max(MIN_ZOOM, 0.1) + 500;

  return (
    <div className="relative w-full h-full bg-surface overflow-hidden">
      <svg
        ref={svgRef}
        className="w-full h-full"
        viewBox={`${-HALF} ${-HALF} ${VIEW_SIZE} ${VIEW_SIZE}`}
        preserveAspectRatio="xMidYMid meet"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        onWheel={handleWheel}
        style={{ cursor: dragging.current ? "grabbing" : "grab", touchAction: "none" }}
      >
        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          {/* Eisenstein integer lattice — flat-top hexagonal grid */}
          <defs>
            <pattern id="hex-grid" width="75" height="43.3" patternUnits="userSpaceOnUse">
              <polygon
                points="25,0 12.5,21.65 -12.5,21.65 -25,0 -12.5,-21.65 12.5,-21.65"
                fill="none" stroke="#342f4a" strokeWidth="0.5"
              />
              <polygon
                points="62.5,21.65 50,43.3 25,43.3 12.5,21.65 25,0 50,0"
                fill="none" stroke="#342f4a" strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect x={-bgExtent} y={-bgExtent} width={bgExtent * 2} height={bgExtent * 2} fill="url(#hex-grid)" />

          {/* Scan boundary — traces hex cell edges */}
          {scanPath && (
            <path
              d={scanPath}
              fill="none"
              stroke="#8b5cf6"
              strokeWidth="1"
              opacity="0.5"
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
        </g>
      </svg>

      {/* Energy HUD */}
      <div className="absolute bottom-4 left-4 right-4">
        <EnergyBar current={energy.current} max={energy.max} />
      </div>
    </div>
  );
}
