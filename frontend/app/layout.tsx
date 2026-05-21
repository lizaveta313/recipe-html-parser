import Link from "next/link";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Recipe HTML Parser",
  description: "Parser engine for eda.rambler.ru recipe HTML pages",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <header className="topbar">
          <Link href="/" className="brand">Recipe HTML Parser</Link>
          <nav>
            <Link href="/">Анализ</Link>
            <Link href="/reports">История</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
