"use client";

import Link from "next/link";
import { useState } from "react";
import { OFERTAS, type Oferta } from "@/lib/ofertas";
import { idSesion, track } from "@/lib/track";

export default function Ofertas({ auditId, dominio }: { auditId: string; dominio: string }) {
  const [abierta, setAbierta] = useState<Oferta | null>(null);
  const [email, setEmail] = useState("");
  const [consiente, setConsiente] = useState(false);
  const [estado, setEstado] = useState<"inicial" | "enviando" | "hecho">("inicial");
  const [error, setError] = useState<string | null>(null);

  function abrir(oferta: Oferta) {
    track("door_click", { door: oferta.id, precio: oferta.precio }, auditId);
    setAbierta(oferta);
    setEstado("inicial");
    setError(null);
  }

  function cerrar() {
    if (abierta && estado !== "hecho") track("lead_modal_close", { door: abierta.id, escribio_email: email.length > 0 }, auditId);
    setAbierta(null);
  }

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    if (!abierta) return;
    if (!consiente) {
      setError("Marca la casilla para que pueda guardar tu email.");
      return;
    }
    setEstado("enviando");
    setError(null);
    try {
      const r = await fetch("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, door: abierta.id, consent: true, audit_id: auditId, session_id: idSesion() }),
      });
      if (!r.ok) {
        const datos = await r.json().catch(() => ({}));
        setError(typeof datos.detail === "string" ? datos.detail : "No se ha podido guardar tu email.");
        setEstado("inicial");
        return;
      }
      track("lead_submit", { door: abierta.id }, auditId);
      setEstado("hecho");
    } catch {
      setError("No se ha podido conectar. Inténtalo de nuevo.");
      setEstado("inicial");
    }
  }

  return (
    <section className="ofertas placa">
      <h2>¿Quieres que te ayude?</h2>
      <p>Puedo corregir los fallos del informe de {dominio}.</p>
      <div className="rejilla">
        {OFERTAS.map((o) => (
          <div key={o.id} className="oferta">
            <h3>{o.titulo}</h3>
            <p>{o.descripcion}</p>
            <p className="precio">{o.precio}</p>
            <button type="button" onClick={() => abrir(o)}>
              {o.boton}
            </button>
          </div>
        ))}
      </div>

      {abierta ? (
        <div className="velo" role="dialog" aria-modal="true" aria-labelledby="titulo-modal" onClick={cerrar}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="cerrar" aria-label="Cerrar" onClick={cerrar}>
              <svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">
                <path d="M5 5l10 10M15 5 5 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
            <h3 id="titulo-modal">{abierta.titulo}</h3>
            {estado === "hecho" ? (
              <p>Gracias. Te escribiré a {email}.</p>
            ) : (
              <form onSubmit={enviar} noValidate>
                <p>{abierta.aviso}</p>
                <label htmlFor="email-oferta">Tu email</label>
                <input
                  id="email-oferta"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <label className="casilla">
                  <input type="checkbox" checked={consiente} onChange={(e) => setConsiente(e.target.checked)} />
                  <span>
                    Acepto que guardes mi email para contactarme sobre esto. <Link href="/privacidad" target="_blank">Privacidad</Link>
                  </span>
                </label>
                {error ? (
                  <p className="error" role="alert">
                    {error}
                  </p>
                ) : null}
                <button type="submit" disabled={estado === "enviando"}>
                  {estado === "enviando" ? "Enviando…" : "Enviar"}
                </button>
              </form>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
