"use client";

import { useMemo } from "react";

// --- Math utilities ---
const SQRT3 = Math.sqrt(3);

/** Eisenstein norm: N(q + rω) = q² - qr + r² */
function eisensteinNorm(q: number, r: number): number {
  return q * q - q * r + r * r;
}

/** p-adic valuation: largest power of p dividing n. Returns 8 for n=0 (∞ cap). */
function vp(n: number, p: number): number {
  if (n === 0) return 8;
  let v = 0;
  let a = Math.abs(n);
  while (a % p === 0) {
    v++;
    a /= p;
  }
  return v;
}

/** Flat-top hex: axial (q,r) → world (x,y) */
function hexToWorld(q: number, r: number, s: number): [number, number] {
  return [1.5 * s * q, SQRT3 * s * (r + q / 2)];
}

/** Single vertex of a flat-top hex */
function hexVertex(cx: number, cy: number, s: number, i: number): [number, number] {
  const angle = (Math.PI / 3) * i;
  return [cx + s * Math.cos(angle), cy + s * Math.sin(angle)];
}

/** SVG points string for a flat-top hex polygon */
function hexPoints(cx: number, cy: number, s: number): string {
  return Array.from({ length: 6 }, (_, i) => {
    const [x, y] = hexVertex(cx, cy, s, i);
    return `${x},${y}`;
  }).join(" ");
}

/** Axial neighbor offsets (flat-top) */
const NEIGHBORS: [number, number][] = [
  [1, 0],
  [0, 1],
  [-1, 1],
  [-1, 0],
  [0, -1],
  [1, -1],
];

/** Generate all hex cells within `radius` rings */
function hexGrid(radius: number): [number, number][] {
  const cells: [number, number][] = [];
  for (let q = -radius; q <= radius; q++) {
    for (let r = -radius; r <= radius; r++) {
      if (Math.abs(q + r) <= radius) cells.push([q, r]);
    }
  }
  return cells;
}

// --- Color schemes ---

interface HexStyle {
  fill: string;
  stroke: string;
  strokeWidth: number;
  glow?: string;
}

/**
 * Design 1: Fractal Sectors
 * Color by N(q,r) mod 6, glow by combined v₂ + v₃ depth.
 * Shows the 6-adic residue structure as a fractal partition.
 */
function fractalSectorStyle(q: number, r: number): HexStyle {
  const N = eisensteinNorm(q, r);
  if (N === 0)
    return {
      fill: "#e2e0f0",
      stroke: "#ffffff",
      strokeWidth: 1.5,
      glow: "rgba(255,255,255,0.5)",
    };

  const residue = ((N % 6) + 6) % 6;
  const v2 = vp(N, 2);
  const v3 = vp(N, 3);
  const depth = Math.min(v2 + v3, 5);

  // 6 hues matching the game's prime type palette
  const hues = [270, 215, 45, 0, 145, 320];
  const hue = hues[residue];
  const lightness = 12 + depth * 10;
  const saturation = 50 + depth * 10;

  return {
    fill: `hsl(${hue}, ${saturation}%, ${lightness}%)`,
    stroke: `hsl(${hue}, ${saturation}%, ${Math.min(lightness + 12, 55)}%)`,
    strokeWidth: 0.3 + depth * 0.4,
    glow:
      depth >= 2
        ? `hsla(${hue}, 80%, 50%, ${0.1 + depth * 0.08})`
        : undefined,
  };
}

/**
 * Design 2: Dual Valuation
 * Hue from N mod 3 (3-adic residue): violet / blue / gold.
 * Brightness from v₂(N). Ring thickness from v₃(N).
 * "Power nodes" where both valuations are high get extra glow.
 */
function dualValuationStyle(q: number, r: number): HexStyle {
  const N = eisensteinNorm(q, r);
  if (N === 0)
    return {
      fill: "#e2e0f0",
      stroke: "#ffffff",
      strokeWidth: 2,
      glow: "rgba(255,255,255,0.6)",
    };

  const v2 = vp(N, 2);
  const v3 = vp(N, 3);
  const residue3 = ((N % 3) + 3) % 3;

  // 3 base hues for 3-adic residue (matching game palette)
  const hues = [270, 215, 42]; // violet, blue, gold
  const hue = hues[residue3];

  // v₂ controls brightness
  const lightness = 8 + Math.min(v2, 5) * 12;
  const saturation = 30 + Math.min(v2, 5) * 14;

  // v₃ controls border emphasis
  const sw = 0.2 + Math.min(v3, 3) * 0.6;
  const strokeHue =
    v3 > 0
      ? `hsl(${hue}, 90%, ${Math.min(lightness + 25, 70)}%)`
      : `hsl(${hue}, 20%, ${lightness + 5}%)`;

  const isPowerNode = v2 >= 2 && v3 >= 1;

  return {
    fill: `hsl(${hue}, ${saturation}%, ${lightness}%)`,
    stroke: strokeHue,
    strokeWidth: sw,
    glow: isPowerNode
      ? `hsla(${hue}, 80%, 55%, 0.4)`
      : v2 >= 3
        ? `hsla(${hue}, 60%, 45%, 0.2)`
        : undefined,
  };
}

/**
 * Design 3: Ultrametric Balls
 * Nested 3-adic neighborhoods B(0, 3⁻ᵏ).
 * Deeper balls = brighter violet. Outside = dim, tinted by residue.
 * Ball boundaries drawn as explicit bright edges.
 */
function ultrametricBallStyle(q: number, r: number): HexStyle {
  const N = eisensteinNorm(q, r);
  if (N === 0)
    return {
      fill: "#e2e0f0",
      stroke: "#ffffff",
      strokeWidth: 2,
      glow: "rgba(226,224,240,0.6)",
    };

  const v3 = vp(N, 3);

  if (v3 >= 3) {
    return {
      fill: "hsl(270, 75%, 42%)",
      stroke: "hsl(270, 85%, 58%)",
      strokeWidth: 1,
      glow: "rgba(139,92,246,0.45)",
    };
  }
  if (v3 >= 2) {
    return {
      fill: "hsl(270, 55%, 26%)",
      stroke: "hsl(270, 65%, 38%)",
      strokeWidth: 0.7,
      glow: "rgba(139,92,246,0.2)",
    };
  }
  if (v3 >= 1) {
    return {
      fill: "hsl(270, 35%, 17%)",
      stroke: "hsl(270, 45%, 25%)",
      strokeWidth: 0.4,
    };
  }

  // Outside all balls — dim, tinted by mod-3 residue
  const r3 = ((N % 3) + 3) % 3;
  const dimHue = r3 === 1 ? 215 : 42;
  return {
    fill: `hsl(${dimHue}, 12%, 10%)`,
    stroke: `hsl(${dimHue}, 18%, 15%)`,
    strokeWidth: 0.2,
  };
}

// --- Boundary edge computation for ultrametric balls ---

interface BoundaryEdge {
  level: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

function computeBallBoundaries(
  cells: [number, number][],
  cellSet: Set<string>,
  hexSize: number,
): BoundaryEdge[] {
  const edges: BoundaryEdge[] = [];

  for (const [q, r] of cells) {
    const N = eisensteinNorm(q, r);
    const v3 = vp(N, 3);

    for (let level = 1; level <= 3; level++) {
      if (v3 < level) continue;

      for (let i = 0; i < 6; i++) {
        const [dq, dr] = NEIGHBORS[i];
        const nq = q + dq;
        const nr = r + dr;
        const nKey = `${nq},${nr}`;

        let neighborInBall = false;
        if (cellSet.has(nKey)) {
          neighborInBall = vp(eisensteinNorm(nq, nr), 3) >= level;
        }

        if (!neighborInBall) {
          const [cx, cy] = hexToWorld(q, r, hexSize);
          const [x1, y1] = hexVertex(cx, cy, hexSize, i);
          const [x2, y2] = hexVertex(cx, cy, hexSize, (i + 1) % 6);
          edges.push({ level, x1, y1, x2, y2 });
        }
      }
    }
  }

  return edges;
}

// --- Component ---

export type PadicMode = "fractal-sectors" | "dual-valuation" | "ultrametric-balls";

interface PadicHexExplorerProps {
  mode: PadicMode;
  radius?: number;
  hexSize?: number;
}

const MODE_LABELS: Record<PadicMode, string> = {
  "fractal-sectors": "6-adic Fractal Sectors",
  "dual-valuation": "Dual Valuation: v\u2082(N) \u00d7 v\u2083(N)",
  "ultrametric-balls": "3-adic Ultrametric Balls",
};

const MODE_DESCRIPTIONS: Record<PadicMode, string> = {
  "fractal-sectors":
    "Color = N(q,r) mod 6. Glow = combined 2-adic + 3-adic depth. Deeper divisibility = brighter.",
  "dual-valuation":
    "Hue = residue mod 3 (violet/blue/gold). Brightness = v\u2082. Border weight = v\u2083. Power nodes glow.",
  "ultrametric-balls":
    "Nested balls B(0, 3\u207B\u1D4F). Deeper = brighter violet. Boundaries trace exact ball edges.",
};

const BALL_BOUNDARY_COLORS = [
  "",
  "rgba(139,92,246,0.5)",
  "rgba(167,139,250,0.7)",
  "rgba(221,214,254,0.9)",
];

export function PadicHexExplorer({
  mode,
  radius = 10,
  hexSize = 18,
}: PadicHexExplorerProps) {
  const cells = useMemo(() => hexGrid(radius), [radius]);

  const cellSet = useMemo(() => {
    const set = new Set<string>();
    for (const [q, r] of cells) set.add(`${q},${r}`);
    return set;
  }, [cells]);

  const styleFn =
    mode === "fractal-sectors"
      ? fractalSectorStyle
      : mode === "dual-valuation"
        ? dualValuationStyle
        : ultrametricBallStyle;

  const ballEdges = useMemo(
    () =>
      mode === "ultrametric-balls"
        ? computeBallBoundaries(cells, cellSet, hexSize)
        : [],
    [cells, cellSet, mode, hexSize],
  );

  const viewExtent = (radius + 2) * hexSize * 2;
  const gap = 1; // pixel gap between hex cells

  return (
    <div className="relative w-full h-full bg-void overflow-hidden">
      <svg
        className="w-full h-full"
        viewBox={`${-viewExtent} ${-viewExtent} ${viewExtent * 2} ${viewExtent * 2}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Glow layer (renders behind) */}
        {cells.map(([q, r]) => {
          const style = styleFn(q, r);
          if (!style.glow) return null;
          const [cx, cy] = hexToWorld(q, r, hexSize);
          return (
            <polygon
              key={`glow-${q},${r}`}
              points={hexPoints(cx, cy, hexSize + 5)}
              fill={style.glow}
            />
          );
        })}

        {/* Hex cells */}
        {cells.map(([q, r]) => {
          const [cx, cy] = hexToWorld(q, r, hexSize);
          const style = styleFn(q, r);
          return (
            <polygon
              key={`hex-${q},${r}`}
              points={hexPoints(cx, cy, hexSize - gap)}
              fill={style.fill}
              stroke={style.stroke}
              strokeWidth={style.strokeWidth}
            />
          );
        })}

        {/* Ball boundary edges (ultrametric mode only) */}
        {ballEdges.map((e, i) => (
          <line
            key={`edge-${i}`}
            x1={e.x1}
            y1={e.y1}
            x2={e.x2}
            y2={e.y2}
            stroke={BALL_BOUNDARY_COLORS[e.level]}
            strokeWidth={0.5 + e.level * 0.8}
            strokeLinecap="round"
          />
        ))}
      </svg>

      {/* Info overlay */}
      <div className="absolute top-4 left-4 max-w-xs">
        <div className="bg-deep/80 backdrop-blur-sm border border-border rounded-lg px-4 py-3">
          <p className="font-ui text-sm text-text-primary">
            {MODE_LABELS[mode]}
          </p>
          <p className="font-data text-xs text-text-muted mt-1">
            {MODE_DESCRIPTIONS[mode]}
          </p>
          <p className="font-data text-[10px] text-text-muted/60 mt-2">
            N(q,r) = q² − qr + r² (Eisenstein norm)
          </p>
        </div>
      </div>
    </div>
  );
}
