import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import { Overpass } from "next/font/google";
import { NOMBRE_SITIO, URL_SITIO } from "@/lib/sitio";
import "./globals.css";

const TITULO = "Auditoría web gratuita para tu negocio";
const DESCRIPCION =
  "Escribe la dirección de tu web y descubre en un minuto qué la frena: velocidad, móvil, Google, textos legales y contacto. Explicado sin tecnicismos.";

export const metadata: Metadata = {
  metadataBase: new URL(URL_SITIO),
  title: { default: TITULO, template: `%s | ${NOMBRE_SITIO}` },
  description: DESCRIPCION,
  // Sin `url` a propósito: lo heredan los informes, y al compartirlos el enlace debe seguir siendo el suyo.
  openGraph: { type: "website", siteName: NOMBRE_SITIO, locale: "es_ES", title: TITULO, description: DESCRIPCION },
  twitter: { card: "summary_large_image" },
};

// Overpass desciende de la tipografía de las señales de carretera. next/font la sirve desde el propio sitio.
const fuente = Overpass({ subsets: ["latin"], variable: "--fuente", display: "swap" });

const umamiSrc = process.env.NEXT_PUBLIC_UMAMI_SRC;
const umamiId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={fuente.variable}>
      <body>
        <header className="cabecera">
          <Link href="/" className="marca">
            Auditoría web
          </Link>
        </header>
        <main>{children}</main>
        <footer className="pie">
          <Link href="/privacidad">Privacidad</Link>
        </footer>
        {process.env.NODE_ENV === "production" ? (
          <Script
            type="module"
            src="https://static.cloudflareinsights.com/beacon.min.js"
            data-cf-beacon='{"token": "a44ce64460a84a7b84e841641b875e54"}'
            strategy="lazyOnload"
          />
        ) : null}
        {umamiSrc && umamiId ? (
          <Script src={umamiSrc} data-website-id={umamiId} strategy="lazyOnload" />
        ) : null}
      </body>
    </html>
  );
}
