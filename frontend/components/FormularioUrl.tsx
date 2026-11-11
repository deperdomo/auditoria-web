"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { iniciarSeguimiento, track, trackUnaVez } from "@/lib/track";

export default function FormularioUrl() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    iniciarSeguimiento();
    trackUnaVez("home_view", "home_view");
  }, []);

  async function enviar(evento: React.FormEvent) {
    evento.preventDefault();
    if (!url.trim() || enviando) return;
    setEnviando(true);
    setError(null);
    track("url_submit", { escrito: url.trim().slice(0, 120) });
    try {
      const r = await fetch("/api/audits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const datos = await r.json().catch(() => ({}));
      if (!r.ok) {
        const mensaje = typeof datos.detail === "string" ? datos.detail : "No se ha podido analizar esa dirección.";
        track("url_error", { codigo: r.status });
        setError(mensaje);
        setEnviando(false);
        return;
      }
      router.push(`/informe/${datos.id}`);
    } catch {
      track("url_error", { codigo: 0 });
      setError("No se ha podido conectar. Inténtalo de nuevo en un momento.");
      setEnviando(false);
    }
  }

  return (
    <form className="formulario" onSubmit={enviar} noValidate>
      <label htmlFor="url" className="oculto">
        Dirección de tu web
      </label>
      <input
        id="url"
        type="text"
        inputMode="url"
        autoComplete="url"
        autoCapitalize="none"
        spellCheck={false}
        placeholder="minegocio.es"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onFocus={() => trackUnaVez("url_focus", "url_focus")}
        aria-describedby={error ? "error-url" : undefined}
      />
      <button type="submit" disabled={enviando}>
        {enviando ? "Analizando…" : "Analizar mi web"}
      </button>
      {error ? (
        <p id="error-url" className="error" role="alert">
          {error}
        </p>
      ) : null}
    </form>
  );
}
