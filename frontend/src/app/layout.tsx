import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Butchery Moderation Lab",
  description: "Un experimento para comprender cómo se interpretan los comentarios académicos.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="es-AR"><body>{children}</body></html>;
}
