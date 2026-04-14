"use client";

import { Button } from "@/components/ui/Button";

interface Decision {
  id: string;
  label: string;
  description?: string;
  cost?: number;
  variant?: "primary" | "secondary" | "danger";
}

interface DecisionPromptProps {
  decisions: Decision[];
  onSelect: (decisionId: string) => void;
}

export function DecisionPrompt({ decisions, onSelect }: DecisionPromptProps) {
  return (
    <div className="border-t border-border bg-deep/80 backdrop-blur-sm px-6 py-4">
      <div className="flex gap-3 items-center">
        <span className="font-ui text-xs text-star tracking-wider uppercase">Decision</span>
        <div className="flex-1" />
        {decisions.map((d) => (
          <div key={d.id} className="flex flex-col items-center gap-1">
            <Button
              variant={d.variant ?? "secondary"}
              size="sm"
              onClick={() => onSelect(d.id)}
            >
              {d.label}
            </Button>
            {d.cost !== undefined && (
              <span className="font-data text-[10px] text-text-muted">
                {d.cost} energy
              </span>
            )}
          </div>
        ))}
      </div>
      {decisions.some((d) => d.description) && (
        <div className="mt-2 flex gap-4">
          {decisions.map((d) =>
            d.description ? (
              <p key={d.id} className="font-ui text-xs text-text-muted flex-1">
                {d.description}
              </p>
            ) : null
          )}
        </div>
      )}
    </div>
  );
}
