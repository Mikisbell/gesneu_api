/**
 * Enterprise Middleware Orchestrator
 * GesNeu Fleet Management API - 2026
 * 
 * Layered Architecture:
 * 1. Security Layer (CORS, Headers)
 * 2. Rate Limiting Layer (Token Bucket)
 * 3. Authentication Layer (NextAuth)
 * 4. Proxy Layer (External APIs)
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { securityLayer } from './middleware/layers/security';
import { rateLimitLayer } from './middleware/layers/rate-limit';
import { proxyLayer } from './middleware/layers/proxy';

/**
 * Public routes that bypass authentication
 */
const PUBLIC_ROUTES = [
    '/api/auth',
    '/api/v1/auth',
    '/api/v1/health',
    '/api/setup-role',
    '/api/maintenance',
    '/api/events', // SSE handles own auth
    '/login',
    '/_next',
    '/favicon.ico',
] as const;

/**
 * Check if route is public
 */
function isPublicRoute(pathname: string): boolean {
    return PUBLIC_ROUTES.some((route) => pathname.startsWith(route));
}

/**
 * Main Middleware Function
 */
export async function proxy(request: NextRequest) {
    const pathname = request.nextUrl.pathname;

    // Add Request ID for tracing
    const requestId = request.headers.get('x-request-id') || crypto.randomUUID();

    // Check if public route FIRST
    if (isPublicRoute(pathname)) {
        // Apply only security layer for public routes
        const response = await securityLayer(request, async () => NextResponse.next());
        response.headers.set('X-Request-ID', requestId);
        response.headers.set('X-Powered-By', 'GesNeu-API-2026');
        return response;
    }

    // Get token for protected routes
    let token = await getToken({
        req: request,
        secret: process.env.NEXTAUTH_SECRET,
        cookieName: process.env.NODE_ENV === 'production' ? '__Secure-authjs.session-token' : 'authjs.session-token',
    });

    if (!token) {
        token = await getToken({
            req: request,
            secret: process.env.NEXTAUTH_SECRET,
            cookieName: 'next-auth.session-token',
        }) || await getToken({
            req: request,
            secret: process.env.NEXTAUTH_SECRET,
            cookieName: '__Secure-next-auth.session-token',
        }) || await getToken({
            req: request,
            secret: process.env.NEXTAUTH_SECRET,
            cookieName: 'authjs.session-token',
        });
    }

    const isAuthPage = pathname.startsWith('/login');
    const isDashboardPage = pathname.startsWith('/dashboard');
    const isProtectedAPI = pathname.startsWith('/api');

    // Redirect authenticated users away from login
    if (isAuthPage && token) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    // Protect dashboard routes
    if (isDashboardPage && !token) {
        const loginUrl = new URL('/login', request.url);
        loginUrl.searchParams.set('callbackUrl', pathname);
        return NextResponse.redirect(loginUrl);
    }

    // Protect API routes
    if (isProtectedAPI && !token) {
        return NextResponse.json(
            { error: 'Unauthorized', message: 'No autenticado: Token requerido' },
            { status: 401 }
        );
    }

    // Apply layered middleware for authenticated routes
    let response = await securityLayer(request, async () => {
        return await rateLimitLayer(
            request,
            async () => {
                return await proxyLayer(request, async () => NextResponse.next());
            },
            token?.sub // Pass user ID for rate limits
        );
    });

    // Add tracing headers
    response.headers.set('X-Request-ID', requestId);
    response.headers.set('X-Powered-By', 'GesNeu-API-2026');

    return response;
}

/**
 * Middleware Configuration
 */
export const config = {
    matcher: [
        /*
         * Match all paths except:
         * - Static files (_next/static, images, etc.)
         * - API routes that handle their own middleware
         */
        '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
};
