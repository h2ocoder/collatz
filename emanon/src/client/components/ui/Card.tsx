import { HTMLAttributes, ReactNode } from "react";

type CardVariant = "default" | "highlighted" | "selected";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  header?: ReactNode;
  children: ReactNode;
}

const variantClasses: Record<CardVariant, string> = {
  default: "bg-surface border border-border",
  highlighted: "bg-surface border border-accent-violet/30",
  selected: "bg-surface border border-accent-violet ring-1 ring-accent-violet/20",
};

export function Card({ variant = "default", header, children, className = "", ...props }: CardProps) {
  return (
    <div className={`rounded-lg p-4 ${variantClasses[variant]} ${className}`} {...props}>
      {header && <div className="flex justify-between items-center mb-3">{header}</div>}
      {children}
    </div>
  );
}
