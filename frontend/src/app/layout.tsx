import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Causal Sentiment Engine",
  description:
    "Agentic sentiment analysis for quant finance — 3D causal factor graph",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-white antialiased">{children}</body>
    </html>
  );
}
