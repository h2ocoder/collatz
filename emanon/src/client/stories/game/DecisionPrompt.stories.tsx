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
