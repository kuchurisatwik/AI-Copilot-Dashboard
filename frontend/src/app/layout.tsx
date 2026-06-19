import type { Metadata } from "next";
import { Inter, Geist } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Trader Copilot AI — Trading Intelligence Platform",
  description:
    "AI-powered trading intelligence and risk management platform. Improve position sizing, validate strategies, and build trading consistency.",
  keywords: [
    "trading",
    "risk management",
    "AI trading coach",
    "position sizing",
    "trade journal",
    "strategy validation",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("dark", "font-sans", geist.variable)}>
      <body className={`${inter.variable} antialiased`}>{children}</body>
    </html>
  );
}
