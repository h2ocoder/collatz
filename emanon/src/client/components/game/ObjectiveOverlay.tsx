"use client";

interface Objective {
  id: string;
  text: string;
  progress?: string;
  completed: boolean;
}

interface ObjectiveOverlayProps {
  current: Objective | null;
}

export function ObjectiveOverlay({ current }: ObjectiveOverlayProps) {
  if (!current) return null;

  return (
    <div className="fixed top-6 left-6 z-50 max-w-xs">
      <div
        className={`
          border-l-2 rounded-r-lg px-4 py-3
          ${current.completed
            ? "border-trust bg-trust/5"
            : "border-accent-violet bg-accent-violet/5"
          }
        `}
      >
        <p
          className={`
            font-narrative text-sm italic
            ${current.completed ? "text-trust line-through opacity-60" : "text-text-primary"}
          `}
        >
          {current.text}
        </p>
        {current.progress && !current.completed && (
          <p className="font-data text-xs text-text-muted mt-1">
            {current.progress}
          </p>
        )}
      </div>
    </div>
  );
}
