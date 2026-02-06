/**
 * Security Configuration - Production-grade CORS and Headers
 * GesNeu API - 2026
 */

export const SECURITY_CONFIG = {
    cors: {
        // Allowed origins por environment
        allowedOrigins: {
            production: [
                process.env.NEXT_PUBLIC_APP_URL || 'https://gesneu.com',
                'https://app.gesneu.com',
                'https://admin.gesneu.com',
            ],
            development: [
                'http://localhost:3000',
                'http://localhost:3005',
                'http://127.0.0.1:3000',
                'http://127.0.0.1:3005',
            ],
            mobile: [
                'capacitor://localhost', // iOS/Android (Capacitor)
                'http://localhost', // Ionic DevApp
            ],
        },

        // Métodos HTTP permitidos
        allowedMethods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],

        // Headers permitidos
        allowedHeaders: [
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'X-Request-ID',
            'X-Tenant-ID',
        ],

        // Headers expuestos al cliente
        exposedHeaders: ['X-Total-Count', 'X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-Request-ID'],

        // Credentials (cookies, auth headers)
        credentials: true,

        // Tiempo de cache del preflight (OPTIONS)
        maxAge: 86400, // 24 hours
    },

    // Security Headers (OWASP Best Practices 2026)
    headers: {
        // Content Security Policy
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"], // TODO: Remove unsafe-* in production
                styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://use.hugeicons.com'],
                fontSrc: ["'self'", 'https://fonts.gstatic.com', 'https://use.hugeicons.com'],
                imgSrc: ["'self'", 'data:', 'https:', 'blob:'],
                connectSrc: ["'self'", 'https://api.gesneu.com', 'wss://events.gesneu.com'],
                frameSrc: ["'none'"],
                objectSrc: ["'none'"],
                upgradeInsecureRequests: [],
            },
        },

        // Strict Transport Security (HSTS)
        strictTransportSecurity: 'max-age=31536000; includeSubDomains; preload',

        // Prevent clickjacking
        xFrameOptions: 'DENY',

        // XSS Protection (legacy, but still good)
        xContentTypeOptions: 'nosniff',

        // Referrer Policy
        referrerPolicy: 'strict-origin-when-cross-origin',

        // Permissions Policy (ex-Feature-Policy)
        permissionsPolicy: {
            camera: [],
            microphone: [],
            geolocation: ['self'],
            payment: [],
        },
    },
} as const;

/**
 * Helper: Get CORS origin based on environment
 */
export function getAllowedOrigins(): string[] {
    const env = process.env.NODE_ENV || 'development';
    const config = SECURITY_CONFIG.cors.allowedOrigins;

    if (env === 'production') {
        return [...config.production] as string[];
    }

    return [...config.development, ...config.mobile];
}

/**
 * Helper: Check if origin is allowed
 */
export function isOriginAllowed(origin: string | null): boolean {
    if (!origin) return false;

    const allowed = getAllowedOrigins();
    return allowed.some((allowedOrigin) => {
        // Exact match
        if (origin === allowedOrigin) return true;

        // Wildcard subdomain support (*.gesneu.com)
        if (allowedOrigin.startsWith('*.')) {
            const domain = allowedOrigin.slice(2);
            return origin.endsWith(domain);
        }

        return false;
    });
}
