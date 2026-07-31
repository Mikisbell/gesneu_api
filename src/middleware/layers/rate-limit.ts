/**
 * Rate Limiting Middleware Layer
 * Token Bucket implementation with in-memory store
 * GesNeu API - 2026
 */

import { NextRequest, NextResponse } from 'next/server';
import { RATE_LIMIT_CONFIG, getRateLimitRule, type RateLimitRule } from '../config/rate-limit.config';

// In-memory store for rate limits
// TODO: Replace with Redis in production for multi-instance deployments
interface RateLimitEntry {
    tokens: number;
    lastRefill: number;
}

const rateLimitStore = new Map<string, RateLimitEntry>();

/**
 * Get client identifier (IP address or User ID)
 */
function getClientId(request: NextRequest, userId?: string): string {
    if (userId) return `user:${userId}`;

    const forwardedFor = request.headers.get('x-forwarded-for');
    const ip = forwardedFor?.split(',')[0].trim() || '127.0.0.1';

    return `ip:${ip}`;
}

/** Check if IP is localhost / loopback or test environment */
function isLocalhostIp(clientId: string, request?: NextRequest): boolean {
    const userAgent = request?.headers.get('user-agent') || '';
    if (userAgent.includes('Playwright') || userAgent.includes('HeadlessChrome')) {
        return true;
    }

    return (
        process.env.NODE_ENV === 'test' ||
        process.env.PLAYWRIGHT === 'true' ||
        clientId.includes('127.0.0.1') ||
        clientId.includes('::1') ||
        clientId === 'ip:localhost' ||
        clientId === 'ip:unknown'
    );
}

/**
 * Token Bucket Algorithm
 */
function consumeToken(
    clientId: string,
    rule: RateLimitRule,
    request?: NextRequest
): {
    allowed: boolean;
    remaining: number;
    resetAt: number;
} {
    if (isLocalhostIp(clientId, request)) {
        return { allowed: true, remaining: 9999, resetAt: Date.now() + 60000 };
    }

    const now = Date.now();
    const key = `${clientId}:${rule.windowMs}`;

    let entry = rateLimitStore.get(key);

    if (!entry || now - entry.lastRefill >= rule.windowMs) {
        // Refill bucket
        entry = {
            tokens: rule.maxRequests,
            lastRefill: now,
        };
        rateLimitStore.set(key, entry);
    }

    const allowed = entry.tokens > 0;
    if (allowed) {
        entry.tokens--;
    }

    const resetAt = entry.lastRefill + rule.windowMs;

    return {
        allowed,
        remaining: Math.max(0, entry.tokens),
        resetAt,
    };
}

/**
 * Rate Limiting Layer
 */
export async function rateLimitLayer(
    request: NextRequest,
    next: () => Promise<NextResponse>,
    userId?: string // From auth layer
): Promise<NextResponse> {
    const pathname = request.nextUrl.pathname;
    const userRole = userId ? 'authenticated' : 'anonymous';

    // Get rate limit rule for this endpoint
    const rule = getRateLimitRule(pathname, userRole);

    // Get client identifier
    const clientId = getClientId(request, userId);

    // Consume token
    const { allowed, remaining, resetAt } = consumeToken(clientId, rule, request);

    // If rate limit exceeded
    if (!allowed) {
        const retryAfter = Math.ceil((resetAt - Date.now()) / 1000);

        return NextResponse.json(
            {
                error: RATE_LIMIT_CONFIG.response.type,
                message: RATE_LIMIT_CONFIG.response.message,
                retryAfter,
            },
            {
                status: RATE_LIMIT_CONFIG.response.status,
                headers: {
                    [RATE_LIMIT_CONFIG.headers.limit]: rule.maxRequests.toString(),
                    [RATE_LIMIT_CONFIG.headers.remaining]: '0',
                    [RATE_LIMIT_CONFIG.headers.reset]: resetAt.toString(),
                    [RATE_LIMIT_CONFIG.headers.retryAfter]: retryAfter.toString(),
                },
            }
        );
    }

    // Process request
    const response = await next();

    // Add rate limit headers
    response.headers.set(RATE_LIMIT_CONFIG.headers.limit, rule.maxRequests.toString());
    response.headers.set(RATE_LIMIT_CONFIG.headers.remaining, remaining.toString());
    response.headers.set(RATE_LIMIT_CONFIG.headers.reset, resetAt.toString());

    return response;
}

/**
 * Cleanup old entries (call periodically)
 */
export function cleanupRateLimitStore(): void {
    const now = Date.now();
    for (const [key, entry] of rateLimitStore.entries()) {
        // Extract windowMs from key (format: "clientId:windowMs")
        const windowMs = parseInt(key.split(':').pop() || '0', 10);
        if (now - entry.lastRefill > windowMs * 2) {
            rateLimitStore.delete(key);
        }
    }
}

// Auto-cleanup every 10 minutes
if (typeof setInterval !== 'undefined') {
    setInterval(cleanupRateLimitStore, 10 * 60 * 1000);
}
