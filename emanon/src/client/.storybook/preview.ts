import type { Preview } from "@storybook/react";
import "../app/globals.css";

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: "void",
      values: [
        { name: "void", value: "#0a0a12" },
        { name: "deep", value: "#0f0f1a" },
        { name: "surface", value: "#1a1520" },
      ],
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};
export default preview;
