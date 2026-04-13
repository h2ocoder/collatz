import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "@/components/ui/Badge";

const meta: Meta<typeof Badge> = {
  title: "UI/Badge",
  component: Badge,
  argTypes: { type: { control: "select", options: ["particle", "force", "field", "law", "story", "witness"] } },
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
      <Badge type="particle" /><Badge type="force" /><Badge type="field" />
      <Badge type="law" /><Badge type="story" /><Badge type="witness" />
    </div>
  ),
};
