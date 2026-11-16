"use client";

import { useCallback, useEffect, useState } from "react";
import { marcarComoPropio } from "@/lib/track";
import { URL_SITIO } from "@/lib/sitio";

// Enlaces para compartir en cada canal: las visitas que entran por ellos salen con su código en «De dónde llegan».
const CANALES = [
  { nombre: "Discord · Emprendosfera", codigo: "dc_empdfra" },
  { nombre: "Discord · midudev", codigo: "dc_midudev" },
];

interface Estadisticas {
  totales: { informes: number; errores: number; eventos: number; emails: number };
  embudo_web: { paso: string; sesiones: number }[];
  embudo_por_grupo: {
    grupo: string; informes: number; abiertos: number; leyeron_mitad: number;
    vieron_ofertas: number; clic_oferta: number; dejaron_email: number;
  }[];
  ofertas: { oferta: string; clics: number; emails: number }[];
  soluciones_mas_abiertas: { id: string; veces: number }[];
  origenes: { origen: string; visitantes: number }[];
  informes: {
    id: string; dominio: string; origen: string; sector: string | null; lote: string | null; nota: number | null;
    creado: string; vistas: number; visitantes: number; desde_movil: number; scroll: number; segundos: number;
    vio_ofertas: boolean; ofertas: string[]; soluciones_abiertas: number; emails: number;
  }[];
  emails: { ts: string; oferta: string; email: string; dominio: string | null }[];
  recientes: { ts: string; evento: string; dominio: string | null; props: Record<string, unknown>; dispositivo: string | null; sesion: string }[];
}

const PASOS: Record<string, string> = {
  home_view: "Entran en la portada",
  url_submit: "Envían una web",
  report_view: "Ven un informe",
  door_view: "Llegan a las ofertas",
  door_click: "Pulsan una oferta",
  lead_submit: "Dejan su email",
};

function pct(parte: number, total: number): string {
  return total ? `${Math.round((parte / total) * 100)} %` : "–";
}

function hora(ts: string): string {
  return new Date(ts).toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export default function Panel() {
  const [token, setToken] = useState("");
  const [datos, setDatos] = useState<Estadisticas | null>(null);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async (t: string) => {
    setError(null);
    try {
      const r = await fetch("/api/admin/stats", { headers: { "X-Admin-Token": t }, cache: "no-store" });
      if (!r.ok) {
        setDatos(null);
        setError(r.status === 403 ? "Token incorrecto (o ADMIN_TOKEN sin configurar en el backend)." : "No se han podido cargar los datos.");
        return;
      }
      setDatos(await r.json());
      marcarComoPropio(); // este navegador es el tuyo: tus visitas dejan de contar
      try {
        sessionStorage.setItem("aw_admin", t);
      } catch {
        /* nada */
      }
    } catch {
      setError("No hay conexión con el backend.");
    }
  }, []);

  async function borrar(id: string, dominio: string) {
    if (!window.confirm(`¿Eliminar el informe de ${dominio}? Se borran también sus visitas registradas y el enlace dejará de funcionar. No se puede deshacer.`)) return;
    const r = await fetch(`/api/admin/audits/${id}`, { method: "DELETE", headers: { "X-Admin-Token": token } }).catch(() => null);
    if (r?.ok) void cargar(token);
    else window.alert("No se ha podido eliminar el informe.");
  }

  useEffect(() => {
    try {
      const guardado = sessionStorage.getItem("aw_admin");
      if (guardado) {
        setToken(guardado);
        void cargar(guardado);
      }
    } catch {
      /* nada */
    }
  }, [cargar]);

  if (!datos) {
    return (
      <section className="estado-pagina">
        <h1>Panel</h1>
        <form className="formulario" onSubmit={(e) => { e.preventDefault(); void cargar(token); }}>
          <label htmlFor="token" className="oculto">Token de administración</label>
          <input id="token" type="password" placeholder="Token de administración" value={token} onChange={(e) => setToken(e.target.value)} />
          <button type="submit">Entrar</button>
          {error ? <p className="error" role="alert">{error}</p> : null}
        </form>
      </section>
    );
  }

  const base = datos.embudo_web[0]?.sesiones ?? 0;
  return (
    <div className="panel">
      <header>
        <h1>Qué hace la gente</h1>
        <button type="button" className="boton-secundario" onClick={() => void cargar(token)}>Actualizar</button>
      </header>

      <div className="cifras">
        <div><strong>{datos.totales.informes}</strong> informes</div>
        <div><strong>{datos.totales.emails}</strong> emails</div>
        <div><strong>{datos.totales.eventos}</strong> acciones registradas</div>
        <div><strong>{datos.totales.errores}</strong> análisis fallidos</div>
      </div>

      <h2>Envíos por sector</h2>
      <p className="nota-pequena">Informes que generaste tú para enviarlos. Cada fila es un sector: aquí se ve cuál responde.</p>
      <div className="tabla"><table>
        <thead><tr><th>Grupo</th><th>Informes</th><th>Abiertos</th><th>Leyeron la mitad</th><th>Vieron ofertas</th><th>Pulsaron oferta</th><th>Dejaron email</th></tr></thead>
        <tbody>
          {datos.embudo_por_grupo.map((g) => (
            <tr key={g.grupo}>
              <td>{g.grupo}</td><td>{g.informes}</td>
              <td>{g.abiertos} <small>{pct(g.abiertos, g.informes)}</small></td>
              <td>{g.leyeron_mitad} <small>{pct(g.leyeron_mitad, g.informes)}</small></td>
              <td>{g.vieron_ofertas} <small>{pct(g.vieron_ofertas, g.informes)}</small></td>
              <td>{g.clic_oferta} <small>{pct(g.clic_oferta, g.informes)}</small></td>
              <td>{g.dejaron_email} <small>{pct(g.dejaron_email, g.informes)}</small></td>
            </tr>
          ))}
          {datos.embudo_por_grupo.length === 0 ? <tr><td colSpan={7}>Aún no hay informes.</td></tr> : null}
        </tbody>
      </table></div>

      <div className="dos-columnas">
        <div>
          <h2>Visitantes que llegan solos</h2>
          <div className="tabla"><table>
            <thead><tr><th>Paso</th><th>Sesiones</th><th>Del total</th></tr></thead>
            <tbody>{datos.embudo_web.map((p) => (
              <tr key={p.paso}><td>{PASOS[p.paso] ?? p.paso}</td><td>{p.sesiones}</td><td>{pct(p.sesiones, base)}</td></tr>
            ))}</tbody>
          </table></div>
        </div>
        <div>
          <h2>Qué oferta interesa</h2>
          <div className="tabla"><table>
            <thead><tr><th>Oferta</th><th>Clics</th><th>Emails</th></tr></thead>
            <tbody>{datos.ofertas.map((o) => (<tr key={o.oferta}><td>{o.oferta}</td><td>{o.clics}</td><td>{o.emails}</td></tr>))}</tbody>
          </table></div>
          <h2>Soluciones más consultadas</h2>
          <div className="tabla"><table>
            <thead><tr><th>Problema</th><th>Veces abierto</th></tr></thead>
            <tbody>
              {datos.soluciones_mas_abiertas.map((s) => (<tr key={s.id}><td>{s.id}</td><td>{s.veces}</td></tr>))}
              {datos.soluciones_mas_abiertas.length === 0 ? <tr><td colSpan={2}>Nadie ha abierto ninguna todavía.</td></tr> : null}
            </tbody>
          </table></div>
        </div>
      </div>

      <h2>De dónde llegan</h2>
      <p className="nota-pequena">Enlaces para compartir por canal. Cada visitante cuenta una vez, aunque no haga nada más.</p>
      <div className="tabla"><table>
        <thead><tr><th>Canal</th><th>Enlace</th><th></th></tr></thead>
        <tbody>{CANALES.map((c) => {
          const enlace = `${URL_SITIO}/?sc=${c.codigo}`;
          return (
            <tr key={c.codigo}>
              <td>{c.nombre}</td><td><code>{enlace}</code></td>
              <td><button type="button" className="boton-secundario" onClick={() => void navigator.clipboard?.writeText(enlace)}>Copiar</button></td>
            </tr>
          );
        })}</tbody>
      </table></div>
      <div className="tabla"><table>
        <thead><tr><th>Origen</th><th>Visitantes</th></tr></thead>
        <tbody>
          {datos.origenes.map((o) => (<tr key={o.origen}><td>{o.origen}</td><td>{o.visitantes}</td></tr>))}
          {datos.origenes.length === 0 ? <tr><td colSpan={2}>Aún no hay visitas.</td></tr> : null}
        </tbody>
      </table></div>

      <h2>Informe a informe</h2>
      <div className="tabla"><table>
        <thead><tr><th>Web</th><th>Sector</th><th>Nota</th><th>Visitas</th><th>Móvil</th><th>Bajó hasta</th><th>Tiempo</th><th>Soluciones</th><th>Ofertas pulsadas</th><th>Email</th><th></th></tr></thead>
        <tbody>{datos.informes.map((i) => (
          <tr key={i.id}>
            <td><a href={`/informe/${i.id}`} target="_blank" rel="noreferrer">{i.dominio}</a></td>
            <td>{i.sector ?? (i.origen === "web" ? "visitante" : "–")}</td>
            <td>{i.nota ?? "–"}</td><td>{i.vistas}</td><td>{i.desde_movil}</td>
            <td>{i.scroll ? `${i.scroll} %` : "–"}</td>
            <td>{i.segundos ? `${i.segundos}+ s` : "–"}</td>
            <td>{i.soluciones_abiertas}</td>
            <td>{i.ofertas.join(", ") || (i.vio_ofertas ? "las vio" : "–")}</td>
            <td>{i.emails ? "sí" : "–"}</td>
            <td><button type="button" className="boton-secundario boton-fila" onClick={() => void borrar(i.id, i.dominio)}>Eliminar</button></td>
          </tr>
        ))}</tbody>
      </table></div>

      <h2>Emails recogidos</h2>
      <div className="tabla"><table>
        <thead><tr><th>Cuándo</th><th>Oferta</th><th>Email</th><th>Web analizada</th></tr></thead>
        <tbody>
          {datos.emails.map((l, n) => (<tr key={n}><td>{hora(l.ts)}</td><td>{l.oferta}</td><td>{l.email}</td><td>{l.dominio ?? "–"}</td></tr>))}
          {datos.emails.length === 0 ? <tr><td colSpan={4}>Ninguno todavía.</td></tr> : null}
        </tbody>
      </table></div>

      <h2>Últimas acciones</h2>
      <div className="tabla"><table>
        <thead><tr><th>Cuándo</th><th>Sesión</th><th>Acción</th><th>Web</th><th>Detalle</th><th>Dispositivo</th></tr></thead>
        <tbody>{datos.recientes.map((e, n) => (
          <tr key={n}>
            <td>{hora(e.ts)}</td><td><code>{e.sesion}</code></td><td>{e.evento}</td><td>{e.dominio ?? "–"}</td>
            <td>{Object.entries(e.props).map(([k, v]) => `${k}: ${String(v)}`).join(" · ") || "–"}</td>
            <td>{e.dispositivo ?? "–"}</td>
          </tr>
        ))}</tbody>
      </table></div>
    </div>
  );
}
