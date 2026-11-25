/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(process.env.STATIC_DASHBOARD === "1" && { output: "export" }),
  async rewrites() {
    const apiBaseUrl = process.env.API_INTERNAL_URL || (process.env.API_HOSTPORT && `http://${process.env.API_HOSTPORT}`);
    if (!apiBaseUrl) return [];
    return [{ source: "/api/:path*", destination: `${apiBaseUrl.replace(/\/$/, "")}/:path*` }];
  },
};

module.exports = nextConfig;
