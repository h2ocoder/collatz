import { Inter, Literata, JetBrains_Mono } from "next/font/google";

export const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["200", "300", "400", "500"],
});

export const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
  weight: ["400"],
});

export const literata = Literata({
  subsets: ["latin"],
  variable: "--font-literata",
  display: "swap",
  weight: ["400"],
  style: ["normal", "italic"],
});
