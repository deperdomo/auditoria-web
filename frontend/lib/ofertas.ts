// La oferta que se muestra al final del informe. Mide cuántos negocios piden ayuda.
export type IdOferta = "gratis";

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
    id: "gratis",
    titulo: "Solo 3 plazas este mes",
    descripcion: "Te ayudo a arreglar lo que frena tu web, sin coste. Déjame tu email y te digo por dónde empezaría.",
    precio: "",
    boton: "Quiero una plaza",
    aviso: "A cambio te pediré tu opinión sincera, permiso para enseñar el antes y el después, y que me recomiendes si quedas contento. Déjame tu email y te escribo.",
  },
];
