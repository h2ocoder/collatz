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
