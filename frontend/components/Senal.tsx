import type { Estado } from "@/lib/tipos";

// Estado dibujado con forma de señal de tráfico, para que no dependa solo del color:
// octógono (pararse a arreglarlo), triángulo (precaución) y círculo (todo en orden).
export default function Senal({ estado }: { estado: Estado }) {
  return (
    <svg className={`senal ${estado}`} viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      {estado === "mal" ? (
        <path d="M5.2 1h5.6L15 5.2v5.6L10.8 15H5.2L1 10.8V5.2z" />
      ) : estado === "mejorable" ? (
        <path d="M8 1.2 15.2 14H.8z" strokeLinejoin="round" />
      ) : (
        <circle cx="8" cy="8" r="7" />
      )}
    </svg>
  );
}
