import type { Meta, StoryObj } from "@storybook/react";
import { Card } from "@/components/ui/Card";

const meta: Meta<typeof Card> = {
  title: "UI/Card",
  component: Card,
  argTypes: { variant: { control: "select", options: ["default", "highlighted", "selected"] } },
};
export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
  args: {
    header: (
      <>
        <span className="font-ui text-sm text-text-primary">Prime 23</span>
        <span className="font-data text-xs text-accent-violet border border-accent-violet/30 px-2 py-0.5 rounded-sm">particle</span>
      </>
    ),
    children: <div className="font-data text-xs text-text-muted leading-relaxed">bloom: sparse · mass: 4 events<br />trust: unknown · energy: —</div>,
  },
};
export const Highlighted: Story = { args: { ...Default.args, variant: "highlighted" } };
export const Selected: Story = { args: { ...Default.args, variant: "selected" } };

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4">
      <Card variant="default" header={<span className="font-ui text-sm">Default</span>}><p className="font-data text-xs text-text-muted">Content</p></Card>
      <Card variant="highlighted" header={<span className="font-ui text-sm">Highlighted</span>}><p className="font-data text-xs text-text-muted">Content</p></Card>
      <Card variant="selected" header={<span className="font-ui text-sm">Selected</span>}><p className="font-data text-xs text-text-muted">Content</p></Card>
    </div>
  ),
};
