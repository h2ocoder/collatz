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
