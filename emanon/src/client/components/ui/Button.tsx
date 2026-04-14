"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--color-accent-violet-15)] border border-[var(--color-accent-violet-40)] text-text-primary hover:bg-[var(--color-accent-violet-30)] transition-colors",
  secondary:
    "border border-border text-text-secondary hover:border-accent-violet/30 hover:text-text-primary transition-colors",
  ghost:
    "text-text-muted underline underline-offset-4 hover:text-text-secondary transition-colors",
  danger:
    "bg-danger/10 border border-danger/40 text-danger hover:bg-danger/20 transition-colors",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-5 py-2.5 text-sm",
  lg: "px-7 py-3 text-base",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", className = "", disabled, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={`font-ui font-normal tracking-wider rounded ${variantClasses[variant]} ${sizeClasses[size]} ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
