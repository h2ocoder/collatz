import type { Meta, StoryObj } from "@storybook/react";
import { EnergyBar } from "@/components/ui/EnergyBar";

const meta: Meta<typeof EnergyBar> = {
  title: "UI/EnergyBar",
  component: EnergyBar,
  args: { max: 100 },
  decorators: [(Story) => <div className="w-64"><Story /></div>],
};
export default meta;
type Story = StoryObj<typeof EnergyBar>;

export const Healthy: Story = { args: { current: 85 } };
export const Warning: Story = { args: { current: 38 } };
export const Critical: Story = { args: { current: 12 } };
export const Empty: Story = { args: { current: 0 } };
export const Full: Story = { args: { current: 100 } };

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-64">
      <EnergyBar current={92} max={100} />
      <EnergyBar current={48} max={100} />
      <EnergyBar current={18} max={100} />
      <EnergyBar current={5} max={100} />
    </div>
  ),
};
