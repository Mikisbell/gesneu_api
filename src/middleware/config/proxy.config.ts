/**
 * Proxy Configuration for External API Integration
 * GesNeu API - 2026
 */

export interface ProxyTarget {
    baseUrl: string;
    timeout?: number;
    headers?: Record<string, string>;
    circuitBreaker?: {
        failureThreshold: number; // Number of failures before opening circuit
        resetTimeout: number; // Time in ms before attempting to close circuit
    };
}

export const PROXY_CONFIG: {
    targets: Record<string, ProxyTarget>;
    routes: Record<string, string>;
    global: {
        includeRequestId: boolean;
        transformResponse: boolean;
        cache: { enabled: boolean; ttl: number };
        retry: { attempts: number; delay: number; backoff: string };
    };
} = {
    // External API targets
    targets: {
        // Tire Suppliers API (example)
        suppliers: {
            baseUrl: process.env.SUPPLIERS_API_URL || 'https://api.suppliers.example.com',
            timeout: 10000, // 10 seconds
            headers: {
                'X-API-Key': process.env.SUPPLIERS_API_KEY || '',
            },
            circuitBreaker: {
                failureThreshold: 5,
                resetTimeout: 60000, // 1 minute
            },
        } as ProxyTarget,

        // Geolocation / Maps API
        maps: {
            baseUrl: process.env.MAPS_API_URL || 'https://maps.googleapis.com/maps/api',
            timeout: 5000,
            headers: {
                'X-API-Key': process.env.GOOGLE_MAPS_API_KEY || '',
            },
            circuitBreaker: {
                failureThreshold: 3,
                resetTimeout: 30000,
            },
        } as ProxyTarget,

        // TPMS (Tire Pressure Monitoring System) API
        tpms: {
            baseUrl: process.env.TPMS_API_URL || 'https://api.tpms-provider.example.com',
            timeout: 8000,
            headers: {
                'Authorization': `Bearer ${process.env.TPMS_API_TOKEN}`,
            },
            circuitBreaker: {
                failureThreshold: 5,
                resetTimeout: 60000,
            },
        } as ProxyTarget,
    },

    // Route mappings (internal -> external)
    routes: {
        '/api/proxy/suppliers': 'suppliers',
        '/api/proxy/maps': 'maps',
        '/api/proxy/tpms': 'tpms',
    } as Record<string, keyof typeof PROXY_CONFIG.targets>,

    // Global proxy settings
    global: {
        // Add request ID for tracing
        includeRequestId: true,

        // Transform response
        transformResponse: true,

        // Cache settings (optional)
        cache: {
            enabled: false, // Enable Redis cache in production
            ttl: 300, // 5 minutes
        },

        // Retry policy
        retry: {
            attempts: 2,
            delay: 1000, // 1 second
            backoff: 'exponential', // exponential or linear
        },
    },
} as const;

/**
 * Helper: Get proxy target for a given route
 */
export function getProxyTarget(pathname: string): ProxyTarget | null {
    for (const [route, targetName] of Object.entries(PROXY_CONFIG.routes)) {
        if (pathname.startsWith(route)) {
            return PROXY_CONFIG.targets[targetName];
        }
    }
    return null;
}

/**
 * Helper: Transform internal path to external path
 */
export function transformProxyPath(internalPath: string): string {
    for (const route of Object.keys(PROXY_CONFIG.routes)) {
        if (internalPath.startsWith(route)) {
            return internalPath.replace(route, '');
        }
    }
    return internalPath;
}
