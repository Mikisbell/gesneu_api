/**
 * 🎯 Next.js 16 Configuration (2026)
 * Optimized for performance and modern features
 */

const withPWA = require('@ducanh2912/next-pwa').default

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ✅ 2026: Experimental features
  experimental: {
    // ppr and reactCompiler removed as they are invalid/moved
  },

  // ✅ TypeScript strict — errores bloquean el build (0 errores al 2026-04-12)
  typescript: {
    ignoreBuildErrors: false,
  },

  // ✅ Next.js 16: Turbopack is default, add empty config to silence warning
  turbopack: {},

  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    remotePatterns: [],
  },

  // PWA Configuration
  // swcMinify removed (default)

  // Sentry integration
  // sentry key removed (handled by wrapper)

  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

// Apply PWA configuration
const pwaConfig = withPWA({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
})

module.exports = pwaConfig(nextConfig);
