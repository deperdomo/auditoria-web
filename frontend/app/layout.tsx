import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Auditoría web gratuita para tu negocio",
  description:
    "Escribe la dirección de tu web y descubre en un minuto qué la frena: velocidad, móvil, Google, textos legales y contacto. Explicado sin tecnicismos.",
};

const umamiSrc = process.env.NEXT_PUBLIC_UMAMI_SRC;
const umamiId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <header className="cabecera">
          <Link href="/" className="marca">
            Auditoría<span>Web</span>
          </Link>
        </header>
        <main>{children}</main>
        <footer className="pie">
          <span>Comprobación automática y orientativa. No sustituye a un asesoramiento técnico o legal.</span>
          <Link href="/privacidad">Privacidad</Link>
        </footer>
        {umamiSrc && umamiId ? (
          <Script src={umamiSrc} data-website-id={umamiId} strategy="afterInteractive" />
        ) : null}
      </body>
    </html>
  );
}
