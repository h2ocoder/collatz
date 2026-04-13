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
