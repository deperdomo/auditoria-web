import type { Metadata } from "next";

export const metadata: Metadata = { title: "Privacidad" };

// PENDIENTE: completa los datos entre corchetes antes de publicar.
export default function Privacidad() {
  return (
    <article className="texto">
      <h1>Privacidad</h1>
      <p>
        <strong>Responsable:</strong> [NOMBRE Y APELLIDOS O RAZÓN SOCIAL], NIF [NIF], [DOMICILIO]. Contacto: [EMAIL].
      </p>
      <h2>Qué datos trato</h2>
      <p>
        <strong>Tu email</strong>, solo si lo escribes para que te avise de un servicio o te envíe un
        presupuesto. Lo uso únicamente para eso, con tu consentimiento, y puedes pedir que lo borre escribiendo
        a [EMAIL].
      </p>
      <p>
        <strong>Uso de la página</strong>: registro de forma anónima qué secciones se ven y qué botones se pulsan,
        para saber si la herramienta resulta útil. No uso cookies ni guardo tu dirección IP. Las visitas se cuentan además con Cloudflare Web
        Analytics, que tampoco usa cookies ni identifica a quien visita la página.
      </p>
      <p>
        <strong>La dirección web que analizas</strong> y el resultado del análisis, que se hace sobre información
        pública de esa web.
      </p>
      <h2>Tus derechos</h2>
      <p>
        Puedes acceder a tus datos, rectificarlos, borrarlos o retirar el consentimiento escribiendo a [EMAIL].
        También puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).
      </p>
    </article>
  );
}
