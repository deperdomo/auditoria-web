import { ImageResponse } from "next/og";

// Imagen que se ve al compartir cualquier enlace del sitio (también los informes). Se genera al compilar.
export const alt = "Auditoría web gratuita para tu negocio";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Imagen() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: 90,
          background: "#1550a8",
          color: "#ffffff",
          border: "14px solid #1550a8",
          outline: "6px solid #ffffff",
          outlineOffset: -26,
        }}
      >
        <div style={{ display: "flex", fontSize: 38, fontWeight: 700 }}>
          Auditoría web
        </div>
        <div style={{ fontSize: 84, fontWeight: 700, lineHeight: 1.1, marginTop: 28 }}>
          ¿Qué está frenando a tu web?
        </div>
        <div style={{ fontSize: 36, color: "#dbe6f7", marginTop: 28 }}>
          Gratis · sin registro · un minuto · sin tecnicismos
        </div>
      </div>
    ),
    size,
  );
}
