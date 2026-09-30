import type { Metadata } from "next";
import { Inter, Oswald, Roboto_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { NavBar } from "@/components/layout/NavBar";
import { Footer } from "@/components/layout/Footer";

const oswald = Oswald({
  variable: "--font-oswald",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const robotoMono = Roboto_Mono({
  variable: "--font-roboto-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Apex Predict — F1 Race Intelligence",
  description: "Predict the race before the lights go out. Leakage-safe ML predictions and Monte Carlo race simulation for Formula 1.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${oswald.variable} ${inter.variable} ${robotoMono.variable} h-full`}
    >
      <body className="flex min-h-full flex-col bg-apex-dark font-sans text-apex-off-white antialiased">
        <Providers>
          <NavBar />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
