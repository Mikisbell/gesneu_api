/**
 * Proxy Middleware Layer
 * Handles forwarding requests to external APIs
 * GesNeu API - 2026
 */

import { NextRequest, NextResponse } from 'next/server';
import { getProxyTarget, transformProxyPath, PROXY_CONFIG, type ProxyTarget } from '../config/proxy.config';

// Circuit Breaker state
interface CircuitState {
    failures: number;
    lastFailureTime: number;
    state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
}

const circuitStates = new Map<string, CircuitState>();

/**
 * Check circuit breaker state
 */
function checkCircuit(targetName: string, target: ProxyTarget): boolean {
    if (!target.circuitBreaker) return true;

    const state = circuitStates.get(targetName) || {
        failures: 0,
        lastFailureTime: 0,
        state: 'CLOSED' as const,
    };

    const now = Date.now();
    const { failureThreshold, resetTimeout } = target.circuitBreaker;

    // If circuit is OPEN, check if we should try again
    if (state.state === 'OPEN') {
        if (now - state.lastFailureTime >= resetTimeout) {
            state.state = 'HALF_OPEN';
            state.failures = 0;
            circuitStates.set(targetName, state);
            return true; // Try one request
        }
        return false; // Circuit still open
    }

    return true; // CLOSED or HALF_OPEN
}

/**
 * Record circuit breaker failure
 */
function recordFailure(targetName: string, target: ProxyTarget): void {
    if (!target.circuitBreaker) return;

    const state = circuitStates.get(targetName) || {
        failures: 0,
        lastFailureTime: 0,
        state: 'CLOSED' as const,
    };

    state.failures++;
    state.lastFailureTime = Date.now();

    if (state.failures >= target.circuitBreaker.failureThreshold) {
        state.state = 'OPEN';
        console.warn(`[Proxy] Circuit breaker OPEN for target: ${targetName}`);
    }

    circuitStates.set(targetName, state);
}

/**
 * Record circuit breaker success
 */
function recordSuccess(targetName: string): void {
    const state = circuitStates.get(targetName);
    if (state) {
        state.failures = 0;
        state.state = 'CLOSED';
        circuitStates.set(targetName, state);
    }
}

/**
 * Proxy a request to external API
 */
async function proxyRequest(
    request: NextRequest,
    target: ProxyTarget,
    targetName: string
): Promise<NextResponse> {
    const internalPath = request.nextUrl.pathname;
    const externalPath = transformProxyPath(internalPath);
    const targetUrl = `${target.baseUrl}${externalPath}${request.nextUrl.search}`;

    // Prepare headers
    const headers = new Headers(request.headers);
    Object.entries(target.headers || {}).forEach(([key, value]) => {
        headers.set(key, value);
    });

    // Add tracing headers
    const requestId = request.headers.get('x-request-id') || crypto.randomUUID();
    headers.set('X-Request-ID', requestId);
    headers.set('X-Forwarded-For', request.headers.get('x-forwarded-for') || 'unknown');
    headers.set('X-Forwarded-Host', request.nextUrl.hostname);

    try {
        // Make request to external API
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), target.timeout || 10000);

        const response = await fetch(targetUrl, {
            method: request.method,
            headers,
            body: request.body,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Record success
        recordSuccess(targetName);

        // Transform response
        const responseHeaders = new Headers(response.headers);
        responseHeaders.set('X-Proxied-By', 'GesNeu-API');
        responseHeaders.set('X-Request-ID', requestId);

        return new NextResponse(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers: responseHeaders,
        });
    } catch (error) {
        // Record failure
        recordFailure(targetName, target);

        console.error(`[Proxy] Error forwarding to ${targetName}:`, error);

        return NextResponse.json(
            {
                error: 'proxy_error',
                message: 'Failed to connect to external service',
                target: targetName,
            },
            { status: 502 } // Bad Gateway
        );
    }
}

/**
 * Proxy Layer Main Function
 */
export async function proxyLayer(
    request: NextRequest,
    next: () => Promise<NextResponse>
): Promise<NextResponse> {
    const pathname = request.nextUrl.pathname;

    // Check if this is a proxy route
    const target = getProxyTarget(pathname);

    if (!target) {
        // Not a proxy route, continue chain
        return next();
    }

    // Determine target name
    const targetEntry = Object.entries(PROXY_CONFIG.routes).find(
        ([route]) => pathname.startsWith(route)
    );
    const targetName = targetEntry?.[1] || 'unknown';

    // Check circuit breaker
    if (!checkCircuit(targetName, target)) {
        return NextResponse.json(
            {
                error: 'service_unavailable',
                message: 'External service temporarily unavailable (circuit breaker open)',
                target: targetName,
            },
            { status: 503 } // Service Unavailable
        );
    }

    // Proxy the request
    return proxyRequest(request, target, targetName);
}
