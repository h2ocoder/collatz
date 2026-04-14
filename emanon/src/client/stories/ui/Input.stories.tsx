import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "@/components/ui/Input";

const meta: Meta<typeof Input> = {
  title: "UI/Input",
  component: Input,
  decorators: [(Story) => <div className="w-80"><Story /></div>],
};
export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = { args: { placeholder: "Enter command...", variant: "default" } };
export const WithLabel: Story = { args: { label: "Prime Address", placeholder: "47", variant: "default" } };
export const Genesis: Story = {
  args: { variant: "genesis", placeholder: "_______" },
  decorators: [
    (Story) => (
      <div className="w-96 text-center">
        <p className="font-data text-text-muted text-sm mb-6">Hello world. I am</p>
        <Story />
      </div>
    ),
  ],
};
