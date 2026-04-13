import type { Meta, StoryObj } from "@storybook/react";
import { PadicHexExplorer } from "@/components/game/PadicHexExplorer";

const meta: Meta<typeof PadicHexExplorer> = {
  title: "Game/PadicHexExplorer",
  component: PadicHexExplorer,
  parameters: { layout: "fullscreen" },
  decorators: [
    (Story) => (
      <div className="h-screen">
        <Story />
      </div>
    ),
  ],
  argTypes: {
    mode: {
      control: "select",
      options: ["fractal-sectors", "dual-valuation", "ultrametric-balls"],
    },
    radius: { control: { type: "range", min: 3, max: 15, step: 1 } },
    hexSize: { control: { type: "range", min: 10, max: 30, step: 1 } },
  },
};
export default meta;

type Story = StoryObj<typeof PadicHexExplorer>;

/** 6-adic residue structure — color by N mod 6, glow by divisibility depth */
export const FractalSectors: Story = {
  args: { mode: "fractal-sectors", radius: 10, hexSize: 18 },
};

/** Independent 2-adic and 3-adic channels — hue from mod 3, brightness from v₂ */
export const DualValuation: Story = {
  args: { mode: "dual-valuation", radius: 10, hexSize: 18 },
};

/** Nested 3-adic balls B(0, 3⁻ᵏ) with explicit boundary edges */
export const UltrametricBalls: Story = {
  args: { mode: "ultrametric-balls", radius: 10, hexSize: 18 },
};

/** Zoomed out — larger radius shows more of the fractal structure */
export const WideView: Story = {
  args: { mode: "fractal-sectors", radius: 15, hexSize: 12 },
};

/** Zoomed in — larger hexes, fewer cells, see individual detail */
export const CloseUp: Story = {
  args: { mode: "dual-valuation", radius: 6, hexSize: 28 },
};
