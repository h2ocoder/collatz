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
