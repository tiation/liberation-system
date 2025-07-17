/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'img.shields.io'],
    unoptimized: true,
  },
  env: {
    LIBERATION_MODE: process.env.LIBERATION_MODE || 'development',
    TRUST_LEVEL: process.env.TRUST_LEVEL || 'maximum',
    API_URL: process.env.API_URL || 'http://localhost:8000',
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
      crypto: false,
    };
    return config;
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
  // GitHub Pages deployment configuration
  ...(process.env.GITHUB_ACTIONS && {
    basePath: '/liberation-system',
    assetPrefix: '/liberation-system',
    trailingSlash: true,
    output: 'export',
  }),
};

module.exports = nextConfig;
