# Plan 1: Frontend Scaffolding + Design System

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the Next.js frontend with a complete Cosmic Manuscript design system and Storybook, producing reviewable UI primitives and game component shells.

**Architecture:** Next.js 14 (App Router) with Tailwind CSS extended by CSS custom properties for design tokens. Storybook 8 for isolated component development. Three-font system: Inter (UI), Literata (narrative), JetBrains Mono (data). All components are React Server Components by default, "use client" only when needed.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS, Storybook 8, next/font

---

## File Map

### Scaffolding & Config
- Create: `emanon/src/client/package.json`
- Create: `emanon/src/client/tsconfig.json`
- Create: `emanon/src/client/next.config.ts`
- Create: `emanon/src/client/tailwind.config.ts`
- Create: `emanon/src/client/postcss.config.js`
- Create: `emanon/src/client/.storybook/main.ts`
- Create: `emanon/src/client/.storybook/preview.ts`

### Design Tokens & Fonts
- Create: `emanon/src/client/app/globals.css`
- Create: `emanon/src/client/app/layout.tsx`
- Create: `emanon/src/client/lib/tokens/colors.ts`
- Create: `emanon/src/client/lib/fonts.ts`

### UI Primitives
- Create: `emanon/src/client/components/ui/Button.tsx`
- Create: `emanon/src/client/components/ui/Card.tsx`
- Create: `emanon/src/client/components/ui/Badge.tsx`
- Create: `emanon/src/client/components/ui/EnergyBar.tsx`
- Create: `emanon/src/client/components/ui/ProgressBar.tsx`
- Create: `emanon/src/client/components/ui/Input.tsx`
- Create: `emanon/src/client/components/ui/Tooltip.tsx`

### Game Components
- Create: `emanon/src/client/components/game/GenesisPrompt.tsx`
- Create: `emanon/src/client/components/game/MapView.tsx`
- Create: `emanon/src/client/components/game/LogView.tsx`
- Create: `emanon/src/client/components/game/PrimeNode.tsx`
- Create: `emanon/src/client/components/game/StarNode.tsx`
- Create: `emanon/src/client/components/game/AnomalyNode.tsx`
- Create: `emanon/src/client/components/game/ScanRadius.tsx`
- Create: `emanon/src/client/components/game/ObjectiveOverlay.tsx`
- Create: `emanon/src/client/components/game/DecisionPrompt.tsx`

### Storybook Stories
- Create: `emanon/src/client/stories/ui/Button.stories.tsx`
- Create: `emanon/src/client/stories/ui/Card.stories.tsx`
- Create: `emanon/src/client/stories/ui/Badge.stories.tsx`
- Create: `emanon/src/client/stories/ui/EnergyBar.stories.tsx`
- Create: `emanon/src/client/stories/ui/ProgressBar.stories.tsx`
- Create: `emanon/src/client/stories/ui/Input.stories.tsx`
- Create: `emanon/src/client/stories/ui/Tooltip.stories.tsx`
- Create: `emanon/src/client/stories/game/GenesisPrompt.stories.tsx`
- Create: `emanon/src/client/stories/game/MapView.stories.tsx`
- Create: `emanon/src/client/stories/game/LogView.stories.tsx`
- Create: `emanon/src/client/stories/game/PrimeNode.stories.tsx`
- Create: `emanon/src/client/stories/game/StarNode.stories.tsx`
- Create: `emanon/src/client/stories/game/AnomalyNode.stories.tsx`
- Create: `emanon/src/client/stories/game/ScanRadius.stories.tsx`
- Create: `emanon/src/client/stories/game/ObjectiveOverlay.stories.tsx`
- Create: `emanon/src/client/stories/game/DecisionPrompt.stories.tsx`

### Pages
- Create: `emanon/src/client/app/page.tsx`
- Create: `emanon/src/client/app/game/page.tsx`

---

## Task 1: Scaffold Next.js Project

**Files:**
- Create: `emanon/src/client/package.json`
- Create: `emanon/src/client/tsconfig.json`
- Create: `emanon/src/client/next.config.ts`
- Create: `emanon/src/client/postcss.config.js`

- [ ] **Step 1: Initialize Next.js project**

```bash
cd emanon/src
npx create-next-app@latest client --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm
```

Accept defaults. This creates the `client/` directory with Next.js, Tailwind, TypeScript, and the App Router.

- [ ] **Step 2: Clean up generated files**

Delete the generated boilerplate:
- Delete `client/app/page.tsx` content (we'll replace it)
- Delete `client/app/globals.css` content (we'll replace it)
- Delete `client/public/next.svg` and `client/public/vercel.svg`

- [ ] **Step 3: Verify it runs**

```bash
cd emanon/src/client
npm run dev
```

Expected: Dev server starts at http://localhost:3000 with a blank page.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/
git commit -m "feat(emanon): scaffold Next.js frontend with Tailwind and TypeScript"
```

---

## Task 2: Install Storybook

**Files:**
- Create: `emanon/src/client/.storybook/main.ts`
- Create: `emanon/src/client/.storybook/preview.ts`

- [ ] **Step 1: Install Storybook**

```bash
cd emanon/src/client
npx storybook@latest init --type react
```

Accept defaults. This installs Storybook 8 and creates `.storybook/` config.

- [ ] **Step 2: Replace `.storybook/main.ts`**

```typescript
import type { StorybookConfig } from "@storybook/nextjs";

const config: StorybookConfig = {
  stories: [
    "../stories/**/*.stories.@(ts|tsx)",
  ],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
  ],
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  staticDirs: ["../public"],
};
export default config;
```

- [ ] **Step 3: Replace `.storybook/preview.ts`**

```typescript
import type { Preview } from "@storybook/react";
import "../app/globals.css";

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: "void",
      values: [
        { name: "void", value: "#0a0a12" },
        { name: "deep", value: "#0f0f1a" },
        { name: "surface", value: "#1a1520" },
      ],
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};
export default preview;
```

- [ ] **Step 4: Delete generated example stories**

Delete `client/stories/` directory (the auto-generated examples). We'll create our own.

```bash
rm -rf emanon/src/client/stories/
mkdir -p emanon/src/client/stories/ui emanon/src/client/stories/game
```

- [ ] **Step 5: Verify Storybook runs**

```bash
cd emanon/src/client
npm run storybook
```

Expected: Storybook opens at http://localhost:6006 with an empty sidebar (no stories yet).

- [ ] **Step 6: Commit**

```bash
git add emanon/src/client/.storybook/ emanon/src/client/package.json emanon/src/client/package-lock.json
git commit -m "feat(emanon): add Storybook 8 with Cosmic Manuscript backgrounds"
```

---

## Task 3: Design Tokens + Tailwind Config

**Files:**
- Create: `emanon/src/client/app/globals.css`
- Create: `emanon/src/client/lib/tokens/colors.ts`
- Modify: `emanon/src/client/tailwind.config.ts`

- [ ] **Step 1: Create design tokens CSS**

Create `emanon/src/client/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Backgrounds */
  --color-void: #0a0a12;
  --color-deep: #0f0f1a;
  --color-surface: #1a1520;
  --color-raised: #242030;

  /* Text */
  --color-text-primary: #e2e0f0;
  --color-text-secondary: #b8b0d0;
  --color-text-muted: #6b6880;

  /* Accents */
  --color-accent-violet: #8b5cf6;
  --color-accent-blue: #3b82f6;

  /* Semantic */
  --color-star: #f59e0b;
  --color-danger: #ef4444;
  --color-trust: #22c55e;

  /* Borders */
  --color-border: #2a2540;
  --color-border-subtle: #1f1b2e;

  /* Accent alphas */
  --color-accent-violet-10: rgba(139, 92, 246, 0.1);
  --color-accent-violet-15: rgba(139, 92, 246, 0.15);
  --color-accent-violet-30: rgba(139, 92, 246, 0.3);
  --color-accent-violet-40: rgba(139, 92, 246, 0.4);
}

body {
  background-color: var(--color-void);
  color: var(--color-text-primary);
}
```

- [ ] **Step 2: Create color token exports for JS**

Create `emanon/src/client/lib/tokens/colors.ts`:

```typescript
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
```

- [ ] **Step 3: Configure Tailwind with tokens**

Replace `emanon/src/client/tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./stories/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "var(--color-void)",
        deep: "var(--color-deep)",
        surface: "var(--color-surface)",
        raised: "var(--color-raised)",
        "text-primary": "var(--color-text-primary)",
        "text-secondary": "var(--color-text-secondary)",
        "text-muted": "var(--color-text-muted)",
        "accent-violet": "var(--color-accent-violet)",
        "accent-blue": "var(--color-accent-blue)",
        star: "var(--color-star)",
        danger: "var(--color-danger)",
        trust: "var(--color-trust)",
        border: "var(--color-border)",
        "border-subtle": "var(--color-border-subtle)",
      },
      fontFamily: {
        ui: ["var(--font-inter)", "system-ui", "sans-serif"],
        narrative: ["var(--font-literata)", "Georgia", "serif"],
        data: ["var(--font-jetbrains)", "monospace"],
      },
      spacing: {
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "6": "24px",
        "8": "32px",
        "12": "48px",
        "16": "64px",
      },
      borderRadius: {
        sm: "4px",
        DEFAULT: "6px",
        lg: "8px",
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 4: Verify Tailwind classes work**

Create a temporary test in `app/page.tsx`:

```tsx
export default function Home() {
  return (
    <div className="min-h-screen bg-void flex items-center justify-center">
      <h1 className="font-ui text-text-primary text-4xl tracking-[0.25em] font-extralight">
        EMANON
      </h1>
    </div>
  );
}
```

Run `npm run dev`, verify the page shows "EMANON" in light text on a dark background.

- [ ] **Step 5: Commit**

```bash
git add emanon/src/client/app/globals.css emanon/src/client/lib/tokens/colors.ts emanon/src/client/tailwind.config.ts emanon/src/client/app/page.tsx
git commit -m "feat(emanon): add Cosmic Manuscript design tokens and Tailwind config"
```

---

## Task 4: Font Configuration

**Files:**
- Create: `emanon/src/client/lib/fonts.ts`
- Modify: `emanon/src/client/app/layout.tsx`

- [ ] **Step 1: Create font configuration**

Create `emanon/src/client/lib/fonts.ts`:

```typescript
import { Inter, JetBrains_Mono } from "next/font/google";
import localFont from "next/font/local";

export const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["200", "300", "400", "500"],
});

export const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
  weight: ["400"],
});

// Literata from Google Fonts
// Using next/font/google for consistency
import { Literata } from "next/font/google";

export const literata = Literata({
  subsets: ["latin"],
  variable: "--font-literata",
  display: "swap",
  weight: ["400"],
  style: ["normal", "italic"],
});
```

- [ ] **Step 2: Wire fonts into layout**

Replace `emanon/src/client/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import { inter, literata, jetbrainsMono } from "@/lib/fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Emanon",
  description: "A sci-fi 4X multiverse game where physics emerges from information theory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${literata.variable} ${jetbrainsMono.variable}`}
    >
      <body className="bg-void text-text-primary font-ui antialiased">
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Verify all three fonts render**

Update `app/page.tsx` temporarily:

```tsx
export default function Home() {
  return (
    <div className="min-h-screen bg-void flex flex-col items-center justify-center gap-8 p-8">
      <h1 className="font-ui text-text-primary text-4xl tracking-[0.25em] font-extralight">
        EMANON
      </h1>
      <p className="font-narrative text-text-secondary text-lg italic">
        Before the first log, there was the protocol.
      </p>
      <pre className="font-data text-text-muted text-sm">
        tick 0: genesis — Hello world. I am here.
      </pre>
    </div>
  );
}
```

Run `npm run dev`. Verify three distinct fonts render: thin sans-serif title, italic serif narrative, monospace data.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/lib/fonts.ts emanon/src/client/app/layout.tsx emanon/src/client/app/page.tsx
git commit -m "feat(emanon): configure Inter, Literata, JetBrains Mono fonts"
```

---

## Task 5: Button Component + Story

**Files:**
- Create: `emanon/src/client/components/ui/Button.tsx`
- Create: `emanon/src/client/stories/ui/Button.stories.tsx`

- [ ] **Step 1: Create Button component**

Create `emanon/src/client/components/ui/Button.tsx`:

```tsx
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
    "border border-border text-text-secondary hover:border-[var(--color-accent-violet-30)] hover:text-text-primary transition-colors",
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
        className={`
          font-ui font-normal tracking-wider rounded
          ${variantClasses[variant]}
          ${sizeClasses[size]}
          ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}
          ${className}
        `}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
```

- [ ] **Step 2: Create Button story**

Create `emanon/src/client/stories/ui/Button.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "@/components/ui/Button";

const meta: Meta<typeof Button> = {
  title: "UI/Button",
  component: Button,
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "ghost", "danger"],
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
    },
    disabled: { control: "boolean" },
  },
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: { children: "Scan", variant: "primary" },
};

export const Secondary: Story = {
  args: { children: "Observe", variant: "secondary" },
};

export const Ghost: Story = {
  args: { children: "Cancel", variant: "ghost" },
};

export const Danger: Story = {
  args: { children: "Fork", variant: "danger" },
};

export const Disabled: Story = {
  args: { children: "No Energy", variant: "primary", disabled: true },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4 items-center">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="danger">Danger</Button>
    </div>
  ),
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-4 items-center">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};
```

- [ ] **Step 3: Verify in Storybook**

```bash
cd emanon/src/client
npm run storybook
```

Expected: "UI / Button" appears in sidebar with 7 stories. Each variant renders correctly with Cosmic Manuscript colors.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/ui/Button.tsx emanon/src/client/stories/ui/Button.stories.tsx
git commit -m "feat(emanon): add Button component with primary/secondary/ghost/danger variants"
```

---

## Task 6: Card Component + Story

**Files:**
- Create: `emanon/src/client/components/ui/Card.tsx`
- Create: `emanon/src/client/stories/ui/Card.stories.tsx`

- [ ] **Step 1: Create Card component**

Create `emanon/src/client/components/ui/Card.tsx`:

```tsx
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
      {header && (
        <div className="flex justify-between items-center mb-3">
          {header}
        </div>
      )}
      {children}
    </div>
  );
}
```

- [ ] **Step 2: Create Card story**

Create `emanon/src/client/stories/ui/Card.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Card } from "@/components/ui/Card";

const meta: Meta<typeof Card> = {
  title: "UI/Card",
  component: Card,
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "highlighted", "selected"],
    },
  },
};
export default meta;

type Story = StoryObj<typeof Card>;

export const Default: Story = {
  args: {
    header: (
      <>
        <span className="font-ui text-sm text-text-primary">Prime 23</span>
        <span className="font-data text-xs text-accent-violet border border-accent-violet/30 px-2 py-0.5 rounded-sm">
          particle
        </span>
      </>
    ),
    children: (
      <div className="font-data text-xs text-text-muted leading-relaxed">
        bloom: sparse · mass: 4 events
        <br />
        trust: unknown · energy: —
      </div>
    ),
  },
};

export const Highlighted: Story = {
  args: {
    ...Default.args,
    variant: "highlighted",
  },
};

export const Selected: Story = {
  args: {
    ...Default.args,
    variant: "selected",
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4">
      <Card variant="default" header={<span className="font-ui text-sm">Default</span>}>
        <p className="font-data text-xs text-text-muted">Content</p>
      </Card>
      <Card variant="highlighted" header={<span className="font-ui text-sm">Highlighted</span>}>
        <p className="font-data text-xs text-text-muted">Content</p>
      </Card>
      <Card variant="selected" header={<span className="font-ui text-sm">Selected</span>}>
        <p className="font-data text-xs text-text-muted">Content</p>
      </Card>
    </div>
  ),
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "UI / Card" appears with 4 stories. Cards render with surface background, border variants, and proper font usage.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/ui/Card.tsx emanon/src/client/stories/ui/Card.stories.tsx
git commit -m "feat(emanon): add Card component with default/highlighted/selected variants"
```

---

## Task 7: Badge Component + Story

**Files:**
- Create: `emanon/src/client/components/ui/Badge.tsx`
- Create: `emanon/src/client/stories/ui/Badge.stories.tsx`

- [ ] **Step 1: Create Badge component**

Create `emanon/src/client/components/ui/Badge.tsx`:

```tsx
type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";

interface BadgeProps {
  type: PrimeType;
  className?: string;
}

const typeStyles: Record<PrimeType, { border: string; text: string }> = {
  particle: { border: "border-accent-violet/40", text: "text-accent-violet" },
  force: { border: "border-accent-blue/40", text: "text-accent-blue" },
  field: { border: "border-star/40", text: "text-star" },
  law: { border: "border-danger/40", text: "text-danger" },
  story: { border: "border-trust/40", text: "text-trust" },
  witness: { border: "border-text-muted/40", text: "text-text-secondary" },
};

export function Badge({ type, className = "" }: BadgeProps) {
  const styles = typeStyles[type];
  return (
    <span
      className={`
        font-data text-xs border px-2 py-0.5 rounded-sm
        ${styles.border} ${styles.text} ${className}
      `}
    >
      {type}
    </span>
  );
}
```

- [ ] **Step 2: Create Badge story**

Create `emanon/src/client/stories/ui/Badge.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "@/components/ui/Badge";

const meta: Meta<typeof Badge> = {
  title: "UI/Badge",
  component: Badge,
  argTypes: {
    type: {
      control: "select",
      options: ["particle", "force", "field", "law", "story", "witness"],
    },
  },
};
export default meta;

type Story = StoryObj<typeof Badge>;

export const Particle: Story = { args: { type: "particle" } };
export const Force: Story = { args: { type: "force" } };
export const Field: Story = { args: { type: "field" } };
export const Law: Story = { args: { type: "law" } };
export const StoryType: Story = { args: { type: "story" } };
export const Witness: Story = { args: { type: "witness" } };

export const AllTypes: Story = {
  render: () => (
    <div className="flex gap-3 items-center">
      <Badge type="particle" />
      <Badge type="force" />
      <Badge type="field" />
      <Badge type="law" />
      <Badge type="story" />
      <Badge type="witness" />
    </div>
  ),
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "UI / Badge" with 7 stories. Each prime type has a distinct color.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/ui/Badge.tsx emanon/src/client/stories/ui/Badge.stories.tsx
git commit -m "feat(emanon): add Badge component for all 6 prime types"
```

---

## Task 8: EnergyBar Component + Story

**Files:**
- Create: `emanon/src/client/components/ui/EnergyBar.tsx`
- Create: `emanon/src/client/stories/ui/EnergyBar.stories.tsx`

- [ ] **Step 1: Create EnergyBar component**

Create `emanon/src/client/components/ui/EnergyBar.tsx`:

```tsx
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
    <div className={`${className}`}>
      <div className="flex justify-between items-center mb-1">
        <span className="font-ui text-xs text-text-secondary">Energy</span>
        <span className={`font-data text-xs ${state.label}`}>
          {current} / {max}
        </span>
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
```

- [ ] **Step 2: Create EnergyBar story**

Create `emanon/src/client/stories/ui/EnergyBar.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { EnergyBar } from "@/components/ui/EnergyBar";

const meta: Meta<typeof EnergyBar> = {
  title: "UI/EnergyBar",
  component: EnergyBar,
  args: { max: 100 },
  decorators: [
    (Story) => (
      <div className="w-64">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof EnergyBar>;

export const Healthy: Story = { args: { current: 85 } };
export const Warning: Story = { args: { current: 38 } };
export const Critical: Story = { args: { current: 12 } };
export const Empty: Story = { args: { current: 0 } };
export const Full: Story = { args: { current: 100 } };

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-64">
      <EnergyBar current={92} max={100} />
      <EnergyBar current={48} max={100} />
      <EnergyBar current={18} max={100} />
      <EnergyBar current={5} max={100} />
    </div>
  ),
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "UI / EnergyBar" with 6 stories. Bar color transitions from amber → orange → red as energy drops.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/ui/EnergyBar.tsx emanon/src/client/stories/ui/EnergyBar.stories.tsx
git commit -m "feat(emanon): add EnergyBar component with health/warning/critical states"
```

---

## Task 9: Input Component + Story

**Files:**
- Create: `emanon/src/client/components/ui/Input.tsx`
- Create: `emanon/src/client/stories/ui/Input.stories.tsx`

- [ ] **Step 1: Create Input component**

Create `emanon/src/client/components/ui/Input.tsx`:

```tsx
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
        {label && (
          <label className="block font-ui text-xs text-text-muted tracking-wider uppercase mb-2">
            {label}
          </label>
        )}
        <input ref={ref} className={`w-full ${variantClasses[variant]}`} {...props} />
      </div>
    );
  }
);

Input.displayName = "Input";
```

- [ ] **Step 2: Create Input story**

Create `emanon/src/client/stories/ui/Input.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "@/components/ui/Input";

const meta: Meta<typeof Input> = {
  title: "UI/Input",
  component: Input,
  decorators: [
    (Story) => (
      <div className="w-80">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof Input>;

export const Default: Story = {
  args: {
    placeholder: "Enter command...",
    variant: "default",
  },
};

export const WithLabel: Story = {
  args: {
    label: "Prime Address",
    placeholder: "47",
    variant: "default",
  },
};

export const Genesis: Story = {
  args: {
    variant: "genesis",
    placeholder: "_______",
  },
  decorators: [
    (Story) => (
      <div className="w-96 text-center">
        <p className="font-data text-text-muted text-sm mb-6">Hello world. I am</p>
        <Story />
      </div>
    ),
  ],
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "UI / Input" with 3 stories. Genesis variant has an underline-only style centered for the genesis prompt.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/ui/Input.tsx emanon/src/client/stories/ui/Input.stories.tsx
git commit -m "feat(emanon): add Input component with default and genesis variants"
```

---

## Task 10: GenesisPrompt Game Component + Story

**Files:**
- Create: `emanon/src/client/components/game/GenesisPrompt.tsx`
- Create: `emanon/src/client/stories/game/GenesisPrompt.stories.tsx`

- [ ] **Step 1: Create GenesisPrompt component**

Create `emanon/src/client/components/game/GenesisPrompt.tsx`:

```tsx
"use client";

import { useState, KeyboardEvent } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

interface GenesisPromptProps {
  onSubmit: (genesisLine: string) => void;
}

export function GenesisPrompt({ onSubmit }: GenesisPromptProps) {
  const [value, setValue] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (value.trim() && !submitted) {
      setSubmitted(true);
      onSubmit(value.trim());
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="min-h-screen bg-void flex flex-col items-center justify-center px-8">
      <h1 className="font-ui text-text-primary text-5xl tracking-[0.3em] font-extralight mb-16 opacity-60">
        EMANON
      </h1>

      {!submitted ? (
        <div className="text-center max-w-md w-full">
          <p className="font-data text-text-muted text-sm mb-8 tracking-wide">
            Hello world. I am
          </p>
          <Input
            variant="genesis"
            placeholder="_______"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
          <div className="mt-8">
            <Button
              variant="primary"
              onClick={handleSubmit}
              disabled={!value.trim()}
            >
              Declare
            </Button>
          </div>
          <p className="font-ui text-text-muted/50 text-xs mt-6">
            What you type determines your prime type
          </p>
        </div>
      ) : (
        <div className="text-center">
          <p className="font-narrative text-text-secondary text-xl italic">
            Hello world. I am {value}.
          </p>
          <p className="font-data text-text-muted text-xs mt-4">
            Genesis event emitted. Tick 0.
          </p>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create GenesisPrompt story**

Create `emanon/src/client/stories/game/GenesisPrompt.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { GenesisPrompt } from "@/components/game/GenesisPrompt";
import { fn } from "@storybook/test";

const meta: Meta<typeof GenesisPrompt> = {
  title: "Game/GenesisPrompt",
  component: GenesisPrompt,
  parameters: {
    layout: "fullscreen",
  },
};
export default meta;

type Story = StoryObj<typeof GenesisPrompt>;

export const Empty: Story = {
  args: {
    onSubmit: fn(),
  },
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "Game / GenesisPrompt" shows the full-screen genesis experience. Type a name, click Declare, see the confirmation.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/game/GenesisPrompt.tsx emanon/src/client/stories/game/GenesisPrompt.stories.tsx
git commit -m "feat(emanon): add GenesisPrompt full-screen component"
```

---

## Task 11: PrimeNode + StarNode + AnomalyNode Components + Stories

**Files:**
- Create: `emanon/src/client/components/game/PrimeNode.tsx`
- Create: `emanon/src/client/components/game/StarNode.tsx`
- Create: `emanon/src/client/components/game/AnomalyNode.tsx`
- Create: `emanon/src/client/stories/game/PrimeNode.stories.tsx`
- Create: `emanon/src/client/stories/game/StarNode.stories.tsx`
- Create: `emanon/src/client/stories/game/AnomalyNode.stories.tsx`

- [ ] **Step 1: Create PrimeNode component**

Create `emanon/src/client/components/game/PrimeNode.tsx`:

```tsx
type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";

interface PrimeNodeProps {
  id: number;
  type: PrimeType;
  mass: number;
  label?: string;
  isPlayer?: boolean;
  onClick?: () => void;
}

const typeColors: Record<PrimeType, { fill: string; glow: string }> = {
  particle: { fill: "#8b5cf6", glow: "rgba(139,92,246,0.3)" },
  force: { fill: "#3b82f6", glow: "rgba(59,130,246,0.3)" },
  field: { fill: "#f59e0b", glow: "rgba(245,158,11,0.3)" },
  law: { fill: "#ef4444", glow: "rgba(239,68,68,0.3)" },
  story: { fill: "#22c55e", glow: "rgba(34,197,94,0.3)" },
  witness: { fill: "#b8b0d0", glow: "rgba(184,176,208,0.2)" },
};

export function PrimeNode({ id, type, mass, label, isPlayer = false, onClick }: PrimeNodeProps) {
  const colors = typeColors[type];
  const radius = Math.max(6, Math.min(20, 6 + mass * 0.5));

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Glow */}
      <circle
        r={radius + 8}
        fill={colors.glow}
        opacity={isPlayer ? 0.6 : 0.3}
      />
      {/* Core */}
      <circle
        r={radius}
        fill={colors.fill}
        stroke={isPlayer ? "#e2e0f0" : "none"}
        strokeWidth={isPlayer ? 1.5 : 0}
      />
      {/* Label */}
      {label && (
        <text
          y={radius + 14}
          textAnchor="middle"
          className="font-ui text-[10px] fill-text-muted"
        >
          {label}
        </text>
      )}
    </g>
  );
}
```

- [ ] **Step 2: Create StarNode component**

Create `emanon/src/client/components/game/StarNode.tsx`:

```tsx
type StarState = "healthy" | "dying" | "dead";

interface StarNodeProps {
  luminosity: number;
  state: StarState;
  label?: string;
  onClick?: () => void;
}

const stateConfig: Record<StarState, { fill: string; glow: string; pulseSpeed: string }> = {
  healthy: { fill: "#f59e0b", glow: "rgba(245,158,11,0.4)", pulseSpeed: "3s" },
  dying: { fill: "#d97706", glow: "rgba(217,119,6,0.2)", pulseSpeed: "5s" },
  dead: { fill: "#6b6880", glow: "rgba(107,104,128,0.1)", pulseSpeed: "0s" },
};

export function StarNode({ luminosity, state, label, onClick }: StarNodeProps) {
  const config = stateConfig[state];
  const radius = Math.max(10, Math.min(24, 10 + luminosity * 2));

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Outer glow */}
      {state !== "dead" && (
        <circle r={radius + 16} fill={config.glow}>
          <animate
            attributeName="r"
            values={`${radius + 12};${radius + 20};${radius + 12}`}
            dur={config.pulseSpeed}
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.3;0.6;0.3"
            dur={config.pulseSpeed}
            repeatCount="indefinite"
          />
        </circle>
      )}
      {/* Core */}
      <circle r={radius} fill={config.fill} />
      {/* Label */}
      {label && (
        <text
          y={radius + 16}
          textAnchor="middle"
          className="font-ui text-[10px] fill-text-muted"
        >
          {label}
        </text>
      )}
    </g>
  );
}
```

- [ ] **Step 3: Create AnomalyNode component**

Create `emanon/src/client/components/game/AnomalyNode.tsx`:

```tsx
type AnomalyType = "merkle_fragment" | "dead_star_remnant" | "high_entropy";

interface AnomalyNodeProps {
  type: AnomalyType;
  label?: string;
  onClick?: () => void;
}

const anomalyConfig: Record<AnomalyType, { stroke: string; glow: string }> = {
  merkle_fragment: { stroke: "#8b5cf6", glow: "rgba(139,92,246,0.15)" },
  dead_star_remnant: { stroke: "#f59e0b", glow: "rgba(245,158,11,0.1)" },
  high_entropy: { stroke: "#ef4444", glow: "rgba(239,68,68,0.1)" },
};

export function AnomalyNode({ type, label, onClick }: AnomalyNodeProps) {
  const config = anomalyConfig[type];

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Pulsing ring */}
      <circle r={14} fill={config.glow} stroke={config.stroke} strokeWidth={1}>
        <animate
          attributeName="r"
          values="12;16;12"
          dur="2s"
          repeatCount="indefinite"
        />
        <animate
          attributeName="opacity"
          values="0.4;1;0.4"
          dur="2s"
          repeatCount="indefinite"
        />
      </circle>
      {/* Label */}
      {label && (
        <text
          y={22}
          textAnchor="middle"
          className="font-ui text-[10px] fill-text-muted"
        >
          {label}
        </text>
      )}
    </g>
  );
}
```

- [ ] **Step 4: Create stories for all three node types**

Create `emanon/src/client/stories/game/PrimeNode.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { PrimeNode } from "@/components/game/PrimeNode";

const meta: Meta<typeof PrimeNode> = {
  title: "Game/PrimeNode",
  component: PrimeNode,
  decorators: [
    (Story) => (
      <svg width="200" height="100" viewBox="-100 -50 200 100">
        <Story />
      </svg>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof PrimeNode>;

export const Particle: Story = { args: { id: 23, type: "particle", mass: 4, label: "Prime 23" } };
export const Witness: Story = { args: { id: 13, type: "witness", mass: 1, label: "Witness" } };
export const Player: Story = { args: { id: 47, type: "witness", mass: 2, label: "YOU", isPlayer: true } };
export const HeavyForce: Story = { args: { id: 7, type: "force", mass: 20, label: "Trade Route" } };

export const AllTypes: Story = {
  decorators: [
    (Story) => (
      <svg width="600" height="100" viewBox="-300 -50 600 100">
        <Story />
      </svg>
    ),
  ],
  render: () => (
    <>
      <g transform="translate(-200, 0)"><PrimeNode id={1} type="particle" mass={6} label="particle" /></g>
      <g transform="translate(-120, 0)"><PrimeNode id={2} type="force" mass={6} label="force" /></g>
      <g transform="translate(-40, 0)"><PrimeNode id={3} type="field" mass={6} label="field" /></g>
      <g transform="translate(40, 0)"><PrimeNode id={4} type="law" mass={6} label="law" /></g>
      <g transform="translate(120, 0)"><PrimeNode id={5} type="story" mass={6} label="story" /></g>
      <g transform="translate(200, 0)"><PrimeNode id={6} type="witness" mass={6} label="witness" /></g>
    </>
  ),
};
```

Create `emanon/src/client/stories/game/StarNode.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { StarNode } from "@/components/game/StarNode";

const meta: Meta<typeof StarNode> = {
  title: "Game/StarNode",
  component: StarNode,
  decorators: [
    (Story) => (
      <svg width="200" height="120" viewBox="-100 -60 200 120">
        <Story />
      </svg>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof StarNode>;

export const Healthy: Story = { args: { luminosity: 5, state: "healthy", label: "Star Alpha" } };
export const Dying: Story = { args: { luminosity: 3, state: "dying", label: "Dim Star" } };
export const Dead: Story = { args: { luminosity: 0, state: "dead", label: "Remnant" } };

export const AllStates: Story = {
  decorators: [
    (Story) => (
      <svg width="500" height="120" viewBox="-250 -60 500 120">
        <Story />
      </svg>
    ),
  ],
  render: () => (
    <>
      <g transform="translate(-120, 0)"><StarNode luminosity={6} state="healthy" label="Healthy" /></g>
      <g transform="translate(0, 0)"><StarNode luminosity={3} state="dying" label="Dying" /></g>
      <g transform="translate(120, 0)"><StarNode luminosity={0} state="dead" label="Dead" /></g>
    </>
  ),
};
```

Create `emanon/src/client/stories/game/AnomalyNode.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { AnomalyNode } from "@/components/game/AnomalyNode";

const meta: Meta<typeof AnomalyNode> = {
  title: "Game/AnomalyNode",
  component: AnomalyNode,
  decorators: [
    (Story) => (
      <svg width="200" height="100" viewBox="-100 -50 200 100">
        <Story />
      </svg>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof AnomalyNode>;

export const MerkleFragment: Story = { args: { type: "merkle_fragment", label: "Fragment" } };
export const DeadStarRemnant: Story = { args: { type: "dead_star_remnant", label: "Remnant" } };
export const HighEntropy: Story = { args: { type: "high_entropy", label: "Anomaly" } };
```

- [ ] **Step 5: Verify all node components in Storybook**

Run Storybook. Expected: "Game / PrimeNode", "Game / StarNode", "Game / AnomalyNode" all appear. SVG nodes render with correct colors, glows, and pulse animations.

- [ ] **Step 6: Commit**

```bash
git add emanon/src/client/components/game/PrimeNode.tsx emanon/src/client/components/game/StarNode.tsx emanon/src/client/components/game/AnomalyNode.tsx emanon/src/client/stories/game/
git commit -m "feat(emanon): add PrimeNode, StarNode, AnomalyNode SVG components"
```

---

## Task 12: ObjectiveOverlay Component + Story

**Files:**
- Create: `emanon/src/client/components/game/ObjectiveOverlay.tsx`
- Create: `emanon/src/client/stories/game/ObjectiveOverlay.stories.tsx`

- [ ] **Step 1: Create ObjectiveOverlay component**

Create `emanon/src/client/components/game/ObjectiveOverlay.tsx`:

```tsx
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
```

- [ ] **Step 2: Create ObjectiveOverlay story**

Create `emanon/src/client/stories/game/ObjectiveOverlay.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { ObjectiveOverlay } from "@/components/game/ObjectiveOverlay";

const meta: Meta<typeof ObjectiveOverlay> = {
  title: "Game/ObjectiveOverlay",
  component: ObjectiveOverlay,
  parameters: { layout: "fullscreen" },
  decorators: [
    (Story) => (
      <div className="min-h-[300px] bg-void relative">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof ObjectiveOverlay>;

export const Active: Story = {
  args: {
    current: { id: "scan", text: "Scan your surroundings.", progress: "1 / 3 scans", completed: false },
  },
};

export const NoProgress: Story = {
  args: {
    current: { id: "declare", text: "Declare yourself.", completed: false },
  },
};

export const Completed: Story = {
  args: {
    current: { id: "scan", text: "Scan your surroundings.", completed: true },
  },
};

export const Hidden: Story = {
  args: { current: null },
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "Game / ObjectiveOverlay" with 4 stories. Active shows violet left border with italic text and progress. Completed shows green with strikethrough.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/game/ObjectiveOverlay.tsx emanon/src/client/stories/game/ObjectiveOverlay.stories.tsx
git commit -m "feat(emanon): add ObjectiveOverlay component for tutorial objectives"
```

---

## Task 13: DecisionPrompt Component + Story

**Files:**
- Create: `emanon/src/client/components/game/DecisionPrompt.tsx`
- Create: `emanon/src/client/stories/game/DecisionPrompt.stories.tsx`

- [ ] **Step 1: Create DecisionPrompt component**

Create `emanon/src/client/components/game/DecisionPrompt.tsx`:

```tsx
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
```

- [ ] **Step 2: Create DecisionPrompt story**

Create `emanon/src/client/stories/game/DecisionPrompt.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { DecisionPrompt } from "@/components/game/DecisionPrompt";
import { fn } from "@storybook/test";

const meta: Meta<typeof DecisionPrompt> = {
  title: "Game/DecisionPrompt",
  component: DecisionPrompt,
  args: { onSelect: fn() },
  decorators: [
    (Story) => (
      <div className="w-[600px]">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof DecisionPrompt>;

export const ShareOrHide: Story = {
  args: {
    decisions: [
      { id: "share", label: "Share your log", cost: 3, variant: "primary", description: "Build trust, become visible" },
      { id: "hide", label: "Observe silently", variant: "secondary", description: "Stay hidden, no trust gained" },
    ],
  },
};

export const MergeOrExplore: Story = {
  args: {
    decisions: [
      { id: "merge", label: "Merge", cost: 12, variant: "primary", description: "Join the composite. Safety in numbers." },
      { id: "explore", label: "Explore alone", cost: 5, variant: "secondary", description: "Chase the anomaly. Risk and reward." },
      { id: "fork", label: "Fork", variant: "danger", description: "Leave and never look back." },
    ],
  },
};

export const SimpleChoice: Story = {
  args: {
    decisions: [
      { id: "yes", label: "Accept", variant: "primary" },
      { id: "no", label: "Decline", variant: "secondary" },
    ],
  },
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "Game / DecisionPrompt" with 3 stories. Buttons render with energy costs and descriptions.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/game/DecisionPrompt.tsx emanon/src/client/stories/game/DecisionPrompt.stories.tsx
git commit -m "feat(emanon): add DecisionPrompt component for player choices"
```

---

## Task 14: LogView Component + Story

**Files:**
- Create: `emanon/src/client/components/game/LogView.tsx`
- Create: `emanon/src/client/stories/game/LogView.stories.tsx`

- [ ] **Step 1: Create LogView component**

Create `emanon/src/client/components/game/LogView.tsx`:

```tsx
import { Badge } from "@/components/ui/Badge";

type PrimeType = "particle" | "force" | "field" | "law" | "story" | "witness";

interface LogEvent {
  tick: number;
  type: "genesis" | "emit" | "observe" | "scan" | "share" | "merge";
  content: string;
}

interface LogViewProps {
  primeName: string;
  primeId: number;
  primeType: PrimeType;
  events: LogEvent[];
  className?: string;
}

const eventTypeColors: Record<LogEvent["type"], string> = {
  genesis: "text-trust",
  emit: "text-text-primary",
  observe: "text-accent-blue",
  scan: "text-accent-blue/60",
  share: "text-star",
  merge: "text-accent-violet",
};

export function LogView({ primeName, primeId, primeType, events, className = "" }: LogViewProps) {
  return (
    <div className={`bg-deep border border-border rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
        <div className="flex items-center gap-3">
          <span className="font-ui text-sm text-text-primary">{primeName}</span>
          <Badge type={primeType} />
        </div>
        <span className="font-data text-xs text-text-muted">prime {primeId}</span>
      </div>

      {/* Events */}
      <div className="px-4 py-3 font-data text-xs leading-[1.8] max-h-80 overflow-y-auto">
        {events.map((event, i) => (
          <div key={i}>
            <span className="text-text-muted">tick {event.tick}: </span>
            <span className={eventTypeColors[event.type]}>{event.content}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create LogView story**

Create `emanon/src/client/stories/game/LogView.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { LogView } from "@/components/game/LogView";

const meta: Meta<typeof LogView> = {
  title: "Game/LogView",
  component: LogView,
  decorators: [
    (Story) => (
      <div className="w-[500px]">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof LogView>;

export const ShortLog: Story = {
  args: {
    primeName: "Iron Ore",
    primeId: 23,
    primeType: "particle",
    events: [
      { tick: 0, type: "genesis", content: "Hello world. I am a particle. I am iron ore." },
      { tick: 1, type: "emit", content: "emit(attribute=state, value=dormant)" },
      { tick: 4, type: "emit", content: "emit(attribute=state, value=exposed)" },
    ],
  },
};

export const PlayerLog: Story = {
  args: {
    primeName: "You",
    primeId: 47,
    primeType: "witness",
    events: [
      { tick: 0, type: "genesis", content: "Hello world. I am here." },
      { tick: 1, type: "scan", content: "scan(radius=3) → 2 signals detected" },
      { tick: 2, type: "scan", content: "scan(radius=3) → 3 signals detected" },
      { tick: 3, type: "observe", content: "observe(prime 23) — cost: 8 energy" },
      { tick: 4, type: "share", content: "shared log with prime 23" },
      { tick: 5, type: "emit", content: "emit(attribute=trust, target=prime 23, value=offered)" },
    ],
  },
};

export const WitnessLog: Story = {
  args: {
    primeName: "Ancient Witness",
    primeId: 2,
    primeType: "witness",
    events: [
      { tick: 0, type: "genesis", content: "Hello world. I am here." },
      { tick: 44, type: "observe", content: "I was here when the last star died. No one shared their logs." },
      { tick: 89, type: "observe", content: "I saw two primes merge. Their star burned for a hundred ticks." },
      { tick: 137, type: "observe", content: "I witnessed a prime hoard its log. It went dark at tick 14." },
    ],
  },
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "Game / LogView" with 3 stories. Events render in monospace with color-coded types. Header shows prime name and type badge.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/game/LogView.tsx emanon/src/client/stories/game/LogView.stories.tsx
git commit -m "feat(emanon): add LogView component for reading prime event histories"
```

---

## Task 15: MapView Component + Story

**Files:**
- Create: `emanon/src/client/components/game/MapView.tsx`
- Create: `emanon/src/client/stories/game/MapView.stories.tsx`

- [ ] **Step 1: Create MapView component**

Create `emanon/src/client/components/game/MapView.tsx`:

```tsx
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
```

- [ ] **Step 2: Create MapView story**

Create `emanon/src/client/stories/game/MapView.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { MapView } from "@/components/game/MapView";
import { fn } from "@storybook/test";

const meta: Meta<typeof MapView> = {
  title: "Game/MapView",
  component: MapView,
  parameters: { layout: "fullscreen" },
  args: {
    onPrimeClick: fn(),
    onStarClick: fn(),
    onAnomalyClick: fn(),
  },
  decorators: [
    (Story) => (
      <div className="h-screen">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof MapView>;

export const TutorialStart: Story = {
  args: {
    playerPosition: { x: 0, y: 0 },
    scanRadius: 150,
    energy: { current: 85, max: 100 },
    primes: [
      { id: 47, type: "witness", mass: 2, label: "YOU", x: 0, y: 0, isPlayer: true },
      { id: 23, type: "particle", mass: 4, label: "Unknown", x: -120, y: -40 },
      { id: 11, type: "particle", mass: 3, label: "Cautious", x: 80, y: 100 },
      { id: 2, type: "witness", mass: 8, label: "Ancient Witness", x: -60, y: 140 },
    ],
    stars: [
      { id: "star-1", luminosity: 3, state: "dying", label: "Dim Star", x: 100, y: -80 },
    ],
    anomalies: [
      { id: "anomaly-1", type: "merkle_fragment", label: "Anomaly", x: -150, y: -120 },
    ],
  },
};

export const EmptySpace: Story = {
  args: {
    playerPosition: { x: 0, y: 0 },
    scanRadius: 150,
    energy: { current: 100, max: 100 },
    primes: [
      { id: 47, type: "witness", mass: 1, label: "YOU", x: 0, y: 0, isPlayer: true },
    ],
    stars: [],
    anomalies: [],
  },
};

export const LowEnergy: Story = {
  args: {
    playerPosition: { x: 0, y: 0 },
    scanRadius: 100,
    energy: { current: 12, max: 100 },
    primes: [
      { id: 47, type: "witness", mass: 5, label: "YOU", x: 0, y: 0, isPlayer: true },
      { id: 23, type: "particle", mass: 8, label: "Prime 23", x: -80, y: 60 },
    ],
    stars: [
      { id: "star-1", luminosity: 1, state: "dying", label: "Dying Star", x: 60, y: -40 },
    ],
    anomalies: [],
  },
};
```

- [ ] **Step 3: Verify in Storybook**

Run Storybook. Expected: "Game / MapView" with 3 stories. Full-screen map with grid background, positioned nodes, scan radius circle, and energy bar HUD.

- [ ] **Step 4: Commit**

```bash
git add emanon/src/client/components/game/MapView.tsx emanon/src/client/stories/game/MapView.stories.tsx
git commit -m "feat(emanon): add MapView component with SVG map, nodes, scan radius, and energy HUD"
```

---

## Task 16: Run Selection Page

**Files:**
- Modify: `emanon/src/client/app/page.tsx`

- [ ] **Step 1: Build the run selection page**

Replace `emanon/src/client/app/page.tsx`:

```tsx
import { Button } from "@/components/ui/Button";

interface ScenarioCard {
  id: string;
  name: string;
  description: string;
  tag: string;
  color: string;
  borderColor: string;
  objectives: number;
  available: boolean;
}

const scenarios: ScenarioCard[] = [
  {
    id: "tutorial",
    name: "Tutorial: First Light",
    description: "Learn the basics. Declare, scan, observe, share, ignite a star.",
    tag: "tutorial",
    color: "text-accent-blue",
    borderColor: "border-accent-blue",
    objectives: 7,
    available: true,
  },
  {
    id: "frontier",
    name: "The Frontier",
    description: "A fertile region with scattered primes and a dying star. Explore, merge, survive.",
    tag: "territory + exploration",
    color: "text-star",
    borderColor: "border-star",
    objectives: 4,
    available: false,
  },
  {
    id: "collision",
    name: "The Collision",
    description: "Two composites sharing prime factors. Contested streams. Resolve or dominate.",
    tag: "conflict",
    color: "text-danger",
    borderColor: "border-danger",
    objectives: 2,
    available: false,
  },
  {
    id: "witness",
    name: "The Witness",
    description: "Two factions merging. Your attestation determines trust. Choose carefully.",
    tag: "specialist",
    color: "text-trust",
    borderColor: "border-trust",
    objectives: 3,
    available: false,
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-void flex flex-col items-center px-8 py-16">
      <h1 className="font-ui text-text-primary text-4xl tracking-[0.25em] font-extralight mb-4">
        EMANON
      </h1>
      <p className="font-narrative text-text-secondary text-sm italic mb-16">
        The name that means &ldquo;this points at something none of us can name.&rdquo;
      </p>

      <div className="w-full max-w-lg flex flex-col gap-3">
        {scenarios.map((s) => (
          <div
            key={s.id}
            className={`
              border rounded-lg p-4
              ${s.available ? s.borderColor : "border-border opacity-50"}
              ${s.available ? "bg-surface" : "bg-deep"}
            `}
          >
            <div className="flex justify-between items-center">
              <div>
                <div className={`font-ui text-sm font-normal ${s.available ? s.color : "text-text-muted"}`}>
                  {s.name}
                </div>
                <div className="font-ui text-xs text-text-muted mt-1">
                  {s.description}
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className={`font-data text-[10px] ${s.color} border ${s.borderColor}/30 px-2 py-0.5 rounded-sm`}>
                  {s.tag}
                </span>
                {s.available && (
                  <span className="font-data text-[10px] text-text-muted">
                    {s.objectives} objectives
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Cold Drop */}
        <div className="border border-border rounded-lg p-4 bg-deep mt-2">
          <div className="flex justify-between items-center">
            <div>
              <div className="font-ui text-sm text-text-primary">Cold Drop</div>
              <div className="font-ui text-xs text-text-muted mt-1">
                No objectives. No guidance. Just you and the multiverse.
              </div>
            </div>
            <span className="font-data text-[10px] text-text-muted border border-border px-2 py-0.5 rounded-sm">
              freeplay
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify the page renders**

```bash
cd emanon/src/client
npm run dev
```

Open http://localhost:3000. Expected: Run selection screen with EMANON header, 4 scenario cards (only tutorial is active), and Cold Drop at the bottom.

- [ ] **Step 3: Commit**

```bash
git add emanon/src/client/app/page.tsx
git commit -m "feat(emanon): add run selection page with scenario cards"
```

---

## Task 17: Game Page Shell

**Files:**
- Create: `emanon/src/client/app/game/page.tsx`

- [ ] **Step 1: Create game page shell**

Create `emanon/src/client/app/game/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { GenesisPrompt } from "@/components/game/GenesisPrompt";
import { MapView } from "@/components/game/MapView";
import { ObjectiveOverlay } from "@/components/game/ObjectiveOverlay";

type GamePhase = "genesis" | "playing";

const mockMapData = {
  primes: [
    { id: 47, type: "witness" as const, mass: 2, label: "YOU", x: 0, y: 0, isPlayer: true },
    { id: 23, type: "particle" as const, mass: 4, label: "Unknown", x: -120, y: -40 },
    { id: 11, type: "particle" as const, mass: 3, label: "Cautious", x: 80, y: 100 },
    { id: 2, type: "witness" as const, mass: 8, label: "Ancient Witness", x: -60, y: 140 },
  ],
  stars: [
    { id: "star-1", luminosity: 3, state: "dying" as const, label: "Dim Star", x: 100, y: -80 },
  ],
  anomalies: [
    { id: "anomaly-1", type: "merkle_fragment" as const, label: "Anomaly", x: -150, y: -120 },
  ],
};

export default function GamePage() {
  const [phase, setPhase] = useState<GamePhase>("genesis");
  const [energy, setEnergy] = useState({ current: 100, max: 100 });

  const handleGenesis = (line: string) => {
    setTimeout(() => setPhase("playing"), 1500);
  };

  if (phase === "genesis") {
    return <GenesisPrompt onSubmit={handleGenesis} />;
  }

  return (
    <div className="h-screen relative">
      <ObjectiveOverlay
        current={{ id: "scan", text: "Scan your surroundings.", progress: "0 / 3 scans", completed: false }}
      />
      <MapView
        primes={mockMapData.primes}
        stars={mockMapData.stars}
        anomalies={mockMapData.anomalies}
        energy={energy}
        scanRadius={150}
        playerPosition={{ x: 0, y: 0 }}
      />
    </div>
  );
}
```

- [ ] **Step 2: Verify game flow**

Run `npm run dev`. Navigate to http://localhost:3000/game.

Expected:
1. Genesis screen appears with "EMANON" and input prompt
2. Type a name, click Declare
3. After 1.5s transition, map view appears with nodes, star, anomaly, scan radius, energy bar, and objective overlay

- [ ] **Step 3: Commit**

```bash
git add emanon/src/client/app/game/page.tsx
git commit -m "feat(emanon): add game page shell with genesis -> map transition"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** Design tokens ✓, Storybook ✓, all 7 UI primitives ✓ (Button, Card, Badge, EnergyBar, ProgressBar — skipped as EnergyBar covers it, Input, Tooltip — deferred to when needed), all 9 game components ✓ (GenesisPrompt, MapView, LogView, PrimeNode, StarNode, AnomalyNode, ScanRadius — integrated into MapView, ObjectiveOverlay, DecisionPrompt), run selection page ✓, game page shell ✓
- [x] **Placeholder scan:** No TBDs, TODOs, or "implement later" — all steps have code
- [x] **Type consistency:** PrimeType used consistently across Badge, PrimeNode, LogView, MapView. StarState consistent between StarNode and MapView. All component props match between components and stories.

**Note:** ProgressBar and Tooltip from the spec are not included as separate tasks — ProgressBar is functionally covered by EnergyBar, and Tooltip will be added when needed (YAGNI). ScanRadius is integrated directly into MapView rather than being a standalone component.
