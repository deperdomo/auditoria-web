import type { Metadata } from "next";
import Informe from "@/components/Informe";

// Los informes hablan de webs de terceros: que no aparezcan en buscadores.
export const metadata: Metadata = {
  title: "Informe de tu web",
  robots: { index: false, follow: false },
};

export default async function PaginaInforme({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <Informe id={id} />;
}
