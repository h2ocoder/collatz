import type { Metadata } from "next";
import { inter, literata, jetbrainsMono } from "@/lib/fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Emanon",
  description: "A sci-fi 4X multiverse game where physics emerges from information theory.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${literata.variable} ${jetbrainsMono.variable}`}
    >
      <body className="bg-void text-text-primary font-ui antialiased">
        {children}
      </body>
    </html>
  );
}
