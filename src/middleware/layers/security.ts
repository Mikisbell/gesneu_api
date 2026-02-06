/**
 * Security Middleware Layer
 * Handles CORS, Security Headers, CSP
 * GesNeu API - 2026
 */

import { NextRequest, NextResponse } from 'next/server';
import { SECURITY_CONFIG, isOriginAllowed } from '../config/security.config';

/**
 * Apply Security Headers to Response
 */
export function applySecurityHeaders(response: NextResponse): NextResponse {
    const { headers } = SECURITY_CONFIG;

    // Content Security Policy
    const csp = Object.entries(headers.contentSecurityPolicy.directives)
        .map(([key, values]) => {
            const directive = key.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);
            return `${directive} ${Array.isArray(values) ? values.join(' ') : values}`;
        })
        .join('; ');

    response.headers.set('Content-Security-Policy', csp);

    // HSTS
    response.headers.set('Strict-Transport-Security', headers.strictTransportSecurity);

    // X-Frame-Options
    response.headers.set('X-Frame-Options', headers.xFrameOptions);

    // X-Content-Type-Options
    response.headers.set('X-Content-Type-Options', headers.xContentTypeOptions);

    // Referrer-Policy
    response.headers.set('Referrer-Policy', headers.referrerPolicy);

    // Permissions-Policy
    const permissionsPolicy = Object.entries(headers.permissionsPolicy)
        .map(([feature, origins]) => {
            const originsStr = Array.isArray(origins) && origins.length > 0 ? `(${origins.join(' ')})` : '()';
            return `${feature}=${originsStr}`;
        })
        .join(', ');
    response.headers.set('Permissions-Policy', permissionsPolicy);

    // Additional Security Headers
    response.headers.set('X-DNS-Prefetch-Control', 'on');
    response.headers.set('X-Download-Options', 'noopen');
    response.headers.set('X-Permitted-Cross-Domain-Policies', 'none');

    return response;
}

/**
 * Handle CORS Preflight and Headers
 */
export function handleCORS(request: NextRequest, response: NextResponse): NextResponse {
    const origin = request.headers.get('origin');
    const { cors } = SECURITY_CONFIG;

    // Handle preflight (OPTIONS)
    if (request.method === 'OPTIONS') {
        const preflightResponse = new NextResponse(null, { status: 204 });

        if (origin && isOriginAllowed(origin)) {
            preflightResponse.headers.set('Access-Control-Allow-Origin', origin);
            preflightResponse.headers.set('Access-Control-Allow-Credentials', cors.credentials.toString());
            preflightResponse.headers.set('Access-Control-Allow-Methods', cors.allowedMethods.join(', '));
            preflightResponse.headers.set('Access-Control-Allow-Headers', cors.allowedHeaders.join(', '));
            preflightResponse.headers.set('Access-Control-Max-Age', cors.maxAge.toString());
        }

        return preflightResponse;
    }

    // Apply CORS headers to normal requests
    if (origin && isOriginAllowed(origin)) {
        response.headers.set('Access-Control-Allow-Origin', origin);
        response.headers.set('Access-Control-Allow-Credentials', cors.credentials.toString());
        response.headers.set('Access-Control-Expose-Headers', cors.exposedHeaders.join(', '));
    }

    return response;
}

/**
 * Security Layer Main Function
 */
export async function securityLayer(
    request: NextRequest,
    next: () => Promise<NextResponse>
): Promise<NextResponse> {
    // Check for OPTIONS preflight
    if (request.method === 'OPTIONS') {
        return handleCORS(request, new NextResponse());
    }

    // Process request through chain
    let response = await next();

    // Apply Security Headers
    response = applySecurityHeaders(response);

    // Apply CORS
    response = handleCORS(request, response);

    return response;
}
