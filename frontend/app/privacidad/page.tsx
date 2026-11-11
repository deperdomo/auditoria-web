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
      <h2>Qué datos tratamos</h2>
      <p>
        <strong>Tu email</strong>, solo si lo escribes para que te avisemos de un servicio o te enviemos un
        presupuesto. Lo usamos únicamente para eso, con tu consentimiento, y puedes pedir que lo borremos escribiendo
        a [EMAIL].
      </p>
      <p>
        <strong>Uso de la página</strong>: registramos de forma anónima qué secciones se ven y qué botones se pulsan,
        para saber si la herramienta resulta útil. No usamos cookies ni guardamos tu dirección IP.
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
