/**
 * Rate Limiting Configuration
 * Token Bucket Algorithm + IP-based throttling
 * GesNeu API - 2026
 */

export interface RateLimitRule {
    windowMs: number; // Time window in milliseconds
    maxRequests: number; // Max requests per window
    skipSuccessfulRequests?: boolean;
    skipFailedRequests?: boolean;
}

export const RATE_LIMIT_CONFIG = {
    // Global rate limits by user type
    global: {
        anonymous: {
            windowMs: 60 * 1000, // 1 minute
            maxRequests: 20,
        } as RateLimitRule,

        authenticated: {
            windowMs: 60 * 1000, // 1 minute
            maxRequests: 100,
        } as RateLimitRule,

        admin: {
            windowMs: 60 * 1000, // 1 minute
            maxRequests: 500,
        } as RateLimitRule,
    },

    // Endpoint-specific overrides
    endpoints: {
        // Login endpoint - strict to prevent brute force
        '/api/auth/login': {
            windowMs: 15 * 60 * 1000, // 15 minutes
            maxRequests: 5,
            skipSuccessfulRequests: true, // Only count failed attempts
        } as RateLimitRule,

        // Register endpoint
        '/api/auth/register': {
            windowMs: 60 * 60 * 1000, // 1 hour
            maxRequests: 3,
        } as RateLimitRule,

        // Password reset
        '/api/auth/forgot-password': {
            windowMs: 60 * 60 * 1000, // 1 hour
            maxRequests: 3,
        } as RateLimitRule,

        // Proxy endpoints (external API calls)
        '/api/proxy/*': {
            windowMs: 60 * 1000, // 1 minute
            maxRequests: 30,
        } as RateLimitRule,

        // File uploads
        '/api/v1/uploads/*': {
            windowMs: 60 * 1000,
            maxRequests: 10,
        } as RateLimitRule,

        // SSE (Server-Sent Events) - more lenient
        '/api/events': {
            windowMs: 60 * 1000,
            maxRequests: 1, // One connection per minute
        } as RateLimitRule,
    },

    // Headers sent to client
    headers: {
        limit: 'X-RateLimit-Limit',
        remaining: 'X-RateLimit-Remaining',
        reset: 'X-RateLimit-Reset',
        retryAfter: 'Retry-After',
    },

    // Response when limit exceeded
    response: {
        status: 429,
        message: 'Too many requests, please try again later.',
        type: 'error',
    },
} as const;

/**
 * Helper: Get rate limit for specific endpoint and user type
 */
export function getRateLimitRule(
    pathname: string,
    userRole: 'anonymous' | 'authenticated' | 'admin' = 'anonymous'
): RateLimitRule {
    // Check for specific endpoint match
    for (const [pattern, rule] of Object.entries(RATE_LIMIT_CONFIG.endpoints)) {
        if (pattern.endsWith('*')) {
            const prefix = pattern.slice(0, -1);
            if (pathname.startsWith(prefix)) {
                return rule;
            }
        } else if (pathname === pattern) {
            return rule;
        }
    }

    // Fall back to global limits
    return RATE_LIMIT_CONFIG.global[userRole];
}
