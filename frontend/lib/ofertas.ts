// Las tres «puertas falsas». Aún no existen: miden si alguien pagaría.
// Los precios son provisionales; cámbialos aquí para probar otros.
export type IdOferta = "pdf" | "vigilancia" | "arreglo";

export interface Oferta {
  id: IdOferta;
  titulo: string;
  descripcion: string;
  precio: string;
  boton: string;
  aviso: string;
}

export const OFERTAS: Oferta[] = [
  {
    id: "pdf",
    titulo: "Informe completo en PDF",
    descripcion: "Todas las comprobaciones con los pasos exactos para corregir cada fallo y el orden en que conviene hacerlo. Listo para pasárselo a quien lleve tu web.",
    precio: "19 € · pago único",
    boton: "Quiero el informe completo",
    aviso: "Todavía lo estamos terminando. Déjanos tu email y te avisamos en cuanto esté, con un 50 % de descuento de lanzamiento.",
  },
  {
    id: "vigilancia",
    titulo: "Vigilancia mensual",
    descripcion: "Revisamos tu web cada mes y te avisamos por email si algo se rompe o empeora, antes de que lo noten tus clientes.",
    precio: "9 € al mes",
    boton: "Quiero que la vigilen",
    aviso: "Este servicio aún no está abierto. Déjanos tu email y te avisamos cuando lo esté, con el primer mes gratis.",
  },
  {
    id: "arreglo",
    titulo: "Que lo arregle un profesional",
    descripcion: "Un desarrollador revisa este informe y te envía un presupuesto cerrado para corregir los fallos.",
    precio: "Presupuesto sin compromiso",
    boton: "Pedir presupuesto",
    aviso: "Déjanos tu email y te escribimos con un presupuesto para esta web.",
  },
];
