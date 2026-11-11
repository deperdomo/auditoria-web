export type Estado = "mal" | "mejorable" | "bien";

export interface Hallazgo {
  id: string;
  estado: Estado;
  titulo: string;
  explicacion: string;
  accion: string;
}

export interface Categoria {
  id: string;
  nombre: string;
  puntuacion: number | null;
  hallazgos: Hallazgo[];
}

export interface Resultado {
  puntuacion: number | null;
  resumen: Record<Estado, number>;
  categorias: Categoria[];
  velocidad_medida: boolean;
  url_final: string | null;
  tecnologia: string | null;
}

export interface Analisis {
  id: string;
  status: "pendiente" | "listo" | "error";
  url: string;
  domain: string;
  created_at: string;
  error: string | null;
  result: Resultado | null;
}
