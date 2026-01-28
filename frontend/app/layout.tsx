/**
 * Root Layout for Next.js App Router
 */

import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Financial Planner",
  description: "AI-powered financial planning assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
