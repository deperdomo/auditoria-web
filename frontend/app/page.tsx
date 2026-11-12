import type { Metadata } from "next";
import FormularioUrl from "@/components/FormularioUrl";
import { NOMBRE_SITIO, URL_SITIO } from "@/lib/sitio";

export const metadata: Metadata = { alternates: { canonical: "/" } };

// Datos estructurados: le dicen a los buscadores qué es esta página.
// ponytail: se vuelca sin escapar porque todo es texto fijo; si algún día entra un dato de fuera, escapar los "<".
const datosEstructurados = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: NOMBRE_SITIO,
  url: URL_SITIO,
  description:
    "Analiza la web de un negocio y explica sin tecnicismos qué la frena: velocidad, móvil, Google, textos legales y contacto.",
  inLanguage: "es",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  offers: { "@type": "Offer", price: "0", priceCurrency: "EUR" },
  author: { "@type": "Person", name: "Deivi Perdomo" },
};

export default function Inicio() {
  return (
    <section className="portada">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(datosEstructurados) }}
      />
      <p className="antetitulo">Gratis · sin registro · un minuto</p>
      <h1>¿Qué está frenando a tu web?</h1>
      <p className="entradilla">
        Escribe la dirección y verás, sin tecnicismos, qué le impide traerte más clientes: velocidad, móvil,
        Google, textos legales y contacto.
      </p>
      <FormularioUrl />
      <ul className="ventajas">
        <li>
          <strong>Explicado para dueños de negocio</strong>
          No verás siglas: verás qué pasa, por qué importa y qué hacer.
        </li>
        <li>
          <strong>Ordenado por importancia</strong>
          Primero lo que te hace perder clientes; lo que está bien, al final.
        </li>
        <li>
          <strong>Con enlace para compartir</strong>
          Pásale el informe a quien lleve tu web.
        </li>
      </ul>
    </section>
  );
}
