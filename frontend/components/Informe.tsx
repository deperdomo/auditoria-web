"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import Ofertas from "@/components/Ofertas";
import { iniciarSeguimiento, track, trackUnaVez } from "@/lib/track";
import type { Analisis, Estado, Hallazgo } from "@/lib/tipos";

const ETIQUETA: Record<Estado, string> = { mal: "Hay que arreglarlo", mejorable: "Mejorable", bien: "Bien" };
const MENSAJES_ESPERA = [
  "Abriendo tu web como lo haría un cliente…",
  "Midiendo cuánto tarda en un móvil…",
  "Mirando cómo la ve Google…",
  "Buscando los textos legales y el contacto…",
  "Preparando el informe…",
];
const UMBRALES_SCROLL = [25, 50, 75, 100];
const UMBRALES_TIEMPO = [15, 30, 60, 120, 300];

function color(nota: number | null): Estado {
  if (nota === null) return "mejorable";
  return nota >= 80 ? "bien" : nota >= 50 ? "mejorable" : "mal";
}

function Tarjeta({ h, auditId }: { h: Hallazgo; auditId: string }) {
  return (
    <li className={`hallazgo ${h.estado}`}>
      <span className="etiqueta">{ETIQUETA[h.estado]}</span>
      <h3>{h.titulo}</h3>
      <p>{h.explicacion}</p>
      {h.estado !== "bien" ? (
        <details
          onToggle={(e) => {
            if ((e.currentTarget as HTMLDetailsElement).open) {
              trackUnaVez(`finding:${auditId}:${h.id}`, "finding_open", { id: h.id, estado: h.estado }, auditId);
            }
          }}
        >
          <summary>Qué hacer</summary>
          <p>{h.accion}</p>
        </details>
      ) : null}
    </li>
  );
}

export default function Informe({ id }: { id: string }) {
  const [datos, setDatos] = useState<Analisis | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);
  const [paso, setPaso] = useState(0);
  const [copiado, setCopiado] = useState(false);
  const inicio = useRef(Date.now());
  const zonaOfertas = useRef<HTMLDivElement | null>(null);

  // Carga del informe (se consulta hasta que termina el análisis)
  useEffect(() => {
    iniciarSeguimiento();
    trackUnaVez(`view:${id}`, "report_view", {}, id);
    let activo = true;
    let intentos = 0;
    let temporizador: ReturnType<typeof setTimeout> | undefined;

    async function consultar() {
      try {
        const r = await fetch(`/api/audits/${id}`, { cache: "no-store" });
        if (!activo) return;
        if (r.status === 404) {
          setFallo("Este informe no existe o ya no está disponible.");
          return;
        }
        const d: Analisis = await r.json();
        if (!activo) return;
        setDatos(d);
        if (d.status === "pendiente") {
          if (intentos++ < 90) temporizador = setTimeout(consultar, 2500);
          else setFallo("El análisis está tardando más de lo normal. Recarga la página en un minuto.");
        } else if (d.status === "listo") {
          trackUnaVez(`ready:${id}`, "report_ready", {
            espera_s: Math.round((Date.now() - inicio.current) / 1000),
            nota: d.result?.puntuacion ?? null,
          }, id);
        } else {
          trackUnaVez(`error:${id}`, "report_error", {}, id);
        }
      } catch {
        if (activo && intentos++ < 90) temporizador = setTimeout(consultar, 4000);
      }
    }
    consultar();
    return () => {
      activo = false;
      if (temporizador) clearTimeout(temporizador);
    };
  }, [id]);

  // Mensajes mientras se espera
  useEffect(() => {
    if (datos?.status !== "pendiente" && datos !== null) return;
    const t = setInterval(() => setPaso((p) => Math.min(p + 1, MENSAJES_ESPERA.length - 1)), 6000);
    return () => clearInterval(t);
  }, [datos]);

  const listo = datos?.status === "listo";

  // Hasta dónde baja, cuánto tiempo lee y si llega a ver las ofertas
  useEffect(() => {
    if (!listo) return;
    const alDesplazar = () => {
      const alto = document.documentElement.scrollHeight;
      const visto = Math.min(100, Math.round(((window.scrollY + window.innerHeight) / alto) * 100));
      for (const u of UMBRALES_SCROLL) {
        if (visto >= u) trackUnaVez(`scroll:${id}:${u}`, "scroll_depth", { pct: u }, id);
      }
    };
    window.addEventListener("scroll", alDesplazar, { passive: true });

    let segundos = 0;
    const reloj = setInterval(() => {
      if (document.visibilityState !== "visible") return;
      segundos += 1;
      if (UMBRALES_TIEMPO.includes(segundos)) trackUnaVez(`t:${id}:${segundos}`, "engaged", { s: segundos }, id);
    }, 1000);

    let observador: IntersectionObserver | undefined;
    if (zonaOfertas.current && "IntersectionObserver" in window) {
      observador = new IntersectionObserver(
        (entradas) => {
          if (entradas.some((e) => e.isIntersecting)) {
            trackUnaVez(`doors:${id}`, "door_view", {}, id);
            observador?.disconnect();
          }
        },
        { threshold: 0.3 },
      );
      observador.observe(zonaOfertas.current);
    }
    return () => {
      window.removeEventListener("scroll", alDesplazar);
      clearInterval(reloj);
      observador?.disconnect();
    };
  }, [listo, id]);

  async function copiarEnlace() {
    track("copy_link", {}, id);
    try {
      await navigator.clipboard.writeText(window.location.origin + window.location.pathname);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    } catch {
      /* el navegador no deja copiar: no pasa nada */
    }
  }

  if (fallo) {
    return (
      <section className="estado-pagina">
        <h1>No hemos podido mostrar el informe</h1>
        <p>{fallo}</p>
        <Link href="/" className="boton-secundario">Analizar otra web</Link>
      </section>
    );
  }

  if (!datos || datos.status === "pendiente") {
    return (
      <section className="estado-pagina" aria-live="polite">
        <div className="girando" aria-hidden="true" />
        <h1>Analizando {datos?.domain ?? "tu web"}</h1>
        <p>{MENSAJES_ESPERA[paso]}</p>
        <p className="nota-pequena">Suele tardar entre 20 y 60 segundos. No cierres la página.</p>
      </section>
    );
  }

  if (datos.status === "error" || !datos.result) {
    return (
      <section className="estado-pagina">
        <h1>No hemos podido analizar {datos.domain}</h1>
        <p>{datos.error ?? "Ha ocurrido un problema inesperado."}</p>
        <Link href="/" className="boton-secundario">Probar con otra dirección</Link>
      </section>
    );
  }

  const r = datos.result;
  const nota = r.puntuacion;
  const urgentes = r.categorias.flatMap((c) => c.hallazgos).filter((h) => h.estado === "mal");

  return (
    <article className="informe">
      <header className="resumen">
        <div className={`dial ${color(nota)}`} style={{ ["--pct" as string]: `${nota ?? 0}%` }}>
          <span>{nota ?? "–"}</span>
          <small>de 100</small>
        </div>
        <div>
          <p className="antetitulo">Informe de</p>
          <h1>{datos.domain}</h1>
          <p className="recuento">
            <span className="punto mal" /> {r.resumen.mal} por arreglar
            <span className="punto mejorable" /> {r.resumen.mejorable} mejorables
            <span className="punto bien" /> {r.resumen.bien} bien
          </p>
          <div className="acciones">
            <button type="button" className="boton-secundario" onClick={copiarEnlace}>
              {copiado ? "Enlace copiado" : "Copiar enlace del informe"}
            </button>
            <Link href="/" className="enlace" onClick={() => track("new_audit_click", {}, id)}>
              Analizar otra web
            </Link>
          </div>
        </div>
      </header>

      {!r.velocidad_medida ? (
        <p className="aviso">No hemos podido medir la velocidad en este análisis. El resto de comprobaciones sí están completas.</p>
      ) : null}

      {r.contenido_dinamico ? (
        <p className="aviso">
          Esta web carga su contenido con JavaScript y desde fuera solo vemos una parte. Por eso no hemos comprobado
          los textos legales ni el contacto: no queremos decirte que falta algo que quizá sí está.
        </p>
      ) : null}

      {urgentes.length > 0 ? (
        <section className="urgentes">
          <h2>Lo primero que arreglaríamos</h2>
          <ol>
            {urgentes.slice(0, 3).map((h) => (
              <li key={h.id}>{h.titulo}</li>
            ))}
          </ol>
        </section>
      ) : null}

      {r.categorias.map((c) => (
        <section key={c.id} className="categoria">
          <h2>
            {c.nombre}
            {c.puntuacion !== null ? <span className={`nota ${color(c.puntuacion)}`}>{c.puntuacion}/100</span> : null}
          </h2>
          <ul>
            {c.hallazgos.map((h) => (
              <Tarjeta key={h.id} h={h} auditId={id} />
            ))}
          </ul>
        </section>
      ))}

      <div ref={zonaOfertas}>
        <Ofertas auditId={id} dominio={datos.domain} />
      </div>
    </article>
  );
}
