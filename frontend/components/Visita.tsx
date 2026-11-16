"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { iniciarSeguimiento, track } from "@/lib/track";

/** Registra cada página vista, aunque el visitante no haga nada más. */
export default function Visita() {
  const ruta = usePathname();
  useEffect(() => {
    if (ruta.startsWith("/admin")) return;
    iniciarSeguimiento();
    track("page_view");
  }, [ruta]);
  return null;
}
