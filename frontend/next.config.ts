import type { NextConfig } from "next";

// El navegador siempre habla con el frontend; este reenvía /api/* al backend.
// Así no hace falta CORS y el backend no se expone a internet.
const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
