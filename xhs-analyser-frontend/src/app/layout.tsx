import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "XHS Insight Studio",
  description: "Prototype frontend for analyzing Xiaohongshu creators.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  );
}
