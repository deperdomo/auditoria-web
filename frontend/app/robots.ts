import type { MetadataRoute } from "next";
import { URL_SITIO } from "@/lib/sitio";

// /informe y /admin no se bloquean aquí: llevan `noindex`, y un buscador solo lo respeta si puede leer la página.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: "/api/" },
    sitemap: `${URL_SITIO}/sitemap.xml`,
  };
}
