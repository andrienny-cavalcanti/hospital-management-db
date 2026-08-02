import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hospital Dra. Yuska | Gestão Hospitalar",
  description:
    "Painel de gestão hospitalar para pacientes, atendimentos, escalas e relatórios.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
