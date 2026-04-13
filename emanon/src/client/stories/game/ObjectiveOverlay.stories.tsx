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
