// Registro de lo que hace cada visitante. Sin cookies ni almacenamiento:
// el identificador de sesión vive solo en memoria y se pierde al recargar.
type Props = Record<string, string | number | boolean | null | undefined>;

declare global {
  interface Window {
    umami?: { track: (nombre: string, datos?: Record<string, unknown>) => void };
  }
}

const CLAVE_NO_SEGUIR = "aw_notrack";
let sesion: string | null = null;
let canal: string | null | undefined; // ?sc= (o utm_source) de la página de entrada; se conserva al navegar
const enviados = new Set<string>();

export function idSesion(): string {
  if (!sesion) {
    sesion =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2) + Date.now().toString(36);
  }
  return sesion;
}

/** Tus propias visitas no cuentan: abre cualquier página con ?notrack=1 (o entra en /admin). */
export function iniciarSeguimiento(): void {
  try {
    const valor = new URLSearchParams(window.location.search).get("notrack");
    if (valor === "1") localStorage.setItem(CLAVE_NO_SEGUIR, "1");
    if (valor === "0") localStorage.removeItem(CLAVE_NO_SEGUIR);
  } catch {
    /* almacenamiento bloqueado: se sigue registrando */
  }
}

export function marcarComoPropio(): void {
  try {
    localStorage.setItem(CLAVE_NO_SEGUIR, "1");
  } catch {
    /* nada */
  }
}

function sinSeguimiento(): boolean {
  try {
    return localStorage.getItem(CLAVE_NO_SEGUIR) === "1";
  } catch {
    return false;
  }
}

/** ?sc= identifica el canal (enlaces del panel); va en la misma columna que utm_source. */
function canalDeEntrada(): string | null {
  if (canal === undefined) {
    const q = new URLSearchParams(window.location.search);
    canal = q.get("sc") ?? q.get("utm_source");
  }
  return canal;
}

export function track(nombre: string, props: Props = {}, auditId?: string): void {
  if (typeof window === "undefined" || sinSeguimiento()) return;
  const cuerpo = JSON.stringify({
    session_id: idSesion(),
    name: nombre,
    audit_id: auditId ?? null,
    props,
    path: window.location.pathname,
    referrer: document.referrer || null,
    utm_source: canalDeEntrada(),
  });
  try {
    const enviado =
      typeof navigator.sendBeacon === "function" &&
      navigator.sendBeacon("/api/events", new Blob([cuerpo], { type: "application/json" }));
    if (!enviado) {
      void fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: cuerpo,
        keepalive: true,
      }).catch(() => undefined);
    }
  } catch {
    /* el registro nunca debe romper la página */
  }
  try {
    window.umami?.track(nombre, { ...props, audit_id: auditId });
  } catch {
    /* nada */
  }
}

/** Igual que track, pero solo una vez por clave (evita duplicados al re-renderizar). */
export function trackUnaVez(clave: string, nombre: string, props: Props = {}, auditId?: string): void {
  if (enviados.has(clave)) return;
  enviados.add(clave);
  track(nombre, props, auditId);
}
