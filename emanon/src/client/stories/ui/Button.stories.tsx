import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "@/components/ui/Button";

const meta: Meta<typeof Button> = {
  title: "UI/Button",
  component: Button,
  argTypes: {
    variant: { control: "select", options: ["primary", "secondary", "ghost", "danger"] },
    size: { control: "select", options: ["sm", "md", "lg"] },
    disabled: { control: "boolean" },
  },
};
export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = { args: { children: "Scan", variant: "primary" } };
export const Secondary: Story = { args: { children: "Observe", variant: "secondary" } };
export const Ghost: Story = { args: { children: "Cancel", variant: "ghost" } };
export const Danger: Story = { args: { children: "Fork", variant: "danger" } };
export const Disabled: Story = { args: { children: "No Energy", variant: "primary", disabled: true } };

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4 items-center">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="danger">Danger</Button>
    </div>
  ),
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-4 items-center">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};
