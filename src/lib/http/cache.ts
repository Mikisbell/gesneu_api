import { NextResponse } from 'next/server';

export interface CacheControlOptions {
    /** s-maxage en segundos para Shared Caches (Cloudflare Edge). Default: 60 */
    sMaxAge?: number;
    /** stale-while-revalidate en segundos. Default: 300 */
    staleWhileRevalidate?: number;
    /** max-age en segundos para el browser del usuario. Default: 0 */
    maxAge?: number;
}

/**
 * Agrega headers de caché optimizados para Cloudflare CDN a un NextResponse.
 *
 * Cloudflare Edge (POPs) almacenará la respuesta en caché durante `sMaxAge` segundos.
 * Durante `staleWhileRevalidate` segundos adicionales, servirá la respuesta en caché antigua
 * instantáneamente mientras revalida en background con el backend Node.js.
 */
export function setEdgeCacheHeaders(
    response: NextResponse,
    options: CacheControlOptions = {}
): NextResponse {
    const {
        sMaxAge = 60,
        staleWhileRevalidate = 300,
        maxAge = 0,
    } = options;

    const cacheHeaderValue = `public, max-age=${maxAge}, s-maxage=${sMaxAge}, stale-while-revalidate=${staleWhileRevalidate}`;

    response.headers.set('Cache-Control', cacheHeaderValue);
    response.headers.set('CDN-Cache-Control', `public, s-maxage=${sMaxAge}`);
    response.headers.set('Cloudflare-CDN-Cache-Control', `public, s-maxage=${sMaxAge}`);

    return response;
}
