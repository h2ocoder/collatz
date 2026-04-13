import type { Meta, StoryObj } from "@storybook/react";
import { MapView } from "@/components/game/MapView";
import { fn } from "storybook/test";

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
