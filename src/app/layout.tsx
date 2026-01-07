
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/components/providers";
import { InstallPrompt } from "@/components/pwa/InstallPrompt";

const inter = Inter({ subsets: ["latin"] });

import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "GesNeu - Gestión de Neumáticos",
  description: "Sistema integral de gestión de neumáticos",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "GesNeu",
  },
  formatDetection: {
    telephone: false,
  },
};

export const viewport: Viewport = {
  themeColor: "#0f172a",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <head>
        <link rel="stylesheet" href="https://use.hugeicons.com/font/icons.css" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/icons/icon.svg" type="image/svg+xml" />
      </head>
      <body className={inter.className}>
        <Providers>
          <InstallPrompt />
          {children}
        </Providers>
      </body>
    </html>
  );
}
