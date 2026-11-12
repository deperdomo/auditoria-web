import type { MetadataRoute } from "next";
import { URL_SITIO } from "@/lib/sitio";

// Solo las páginas públicas; los informes hablan de webs de terceros y no se indexan.
export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: `${URL_SITIO}/` }, { url: `${URL_SITIO}/privacidad` }];
}
