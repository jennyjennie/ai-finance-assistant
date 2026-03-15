import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Finance Assistant",
  description: "Ask questions about stocks, markets, and economic indicators",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "sans-serif", background: "#f5f5f5" }}>
        {children}
      </body>
    </html>
  );
}
