"use client";

import { InputHTMLAttributes, forwardRef } from "react";

type InputVariant = "default" | "genesis";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  variant?: InputVariant;
  label?: string;
}

const variantClasses: Record<InputVariant, string> = {
  default:
    "bg-raised border border-border text-text-primary font-data text-sm px-4 py-2.5 rounded focus:border-accent-violet/50 focus:outline-none focus:ring-1 focus:ring-accent-violet/20 transition-colors",
  genesis:
    "bg-transparent border-b border-text-muted text-text-primary font-narrative text-xl text-center py-2 focus:border-accent-violet focus:outline-none transition-colors placeholder:text-text-muted/50",
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ variant = "default", label, className = "", ...props }, ref) => {
    return (
      <div className={className}>
        {label && <label className="block font-ui text-xs text-text-muted tracking-wider uppercase mb-2">{label}</label>}
        <input ref={ref} className={`w-full ${variantClasses[variant]}`} {...props} />
      </div>
    );
  }
);

Input.displayName = "Input";
