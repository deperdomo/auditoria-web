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
    titulo: "Te arreglo los fallos gratis",
    descripcion: "Estoy ayudando gratis a unos pocos negocios de Madrid a cambio de su opinión. Déjame tu email y te digo qué arreglaría primero.",
    precio: "Gratis. Solo 5 plazas este mes.",
    boton: "Quiero una plaza",
    aviso: "A cambio te pediré tu opinión sincera, permiso para enseñar el antes y el después, y que me recomiendes si quedas contento. Déjame tu email y te escribo.",
  },
];
