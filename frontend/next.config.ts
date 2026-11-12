import type { NextConfig } from "next";

// El navegador siempre habla con el frontend; este reenvía /api/* al backend.
// Así no hace falta CORS y el backend no se expone a internet.
const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // Quien entra por http:// pasa a https://. Cloudflare avisa del esquema original en `cf-visitor`;
  // en local esa cabecera no existe y no se redirige nada.
  async redirects() {
    return [{
      source: "/:ruta*",
      has: [
        { type: "header", key: "cf-visitor", value: '.*"scheme":"http".*' },
        { type: "host", value: "(?<dominio>.*)" },
      ],
      destination: "https://:dominio/:ruta*",
      permanent: true,
    }];
  },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
