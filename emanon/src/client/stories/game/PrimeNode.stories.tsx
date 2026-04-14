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
