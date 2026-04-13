export const colors = {
  void: "#0a0a12",
  deep: "#0f0f1a",
  surface: "#1a1520",
  raised: "#242030",
  textPrimary: "#e2e0f0",
  textSecondary: "#b8b0d0",
  textMuted: "#6b6880",
  accentViolet: "#8b5cf6",
  accentBlue: "#3b82f6",
  star: "#f59e0b",
  danger: "#ef4444",
  trust: "#22c55e",
  border: "#2a2540",
  borderSubtle: "#1f1b2e",
} as const;

export type ColorToken = keyof typeof colors;
