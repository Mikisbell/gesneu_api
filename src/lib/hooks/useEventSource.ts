'use client';

import { useEffect, useCallback, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface SSEEvent {
    type: 'connected' | 'invalidate' | 'alert' | string;
    queryKeys?: string[];
    data?: any;
    timestamp: number;
}

interface UseEventSourceOptions {
    onConnect?: () => void;
    onError?: (error: Event) => void;
    enabled?: boolean;
    maxRetries?: number;
}

/**
 * Hook to connect to SSE endpoint and automatically invalidate queries
 */
export function useEventSource(options: UseEventSourceOptions = {}) {
    const { onConnect, onError, enabled = true, maxRetries = 3 } = options;
    const queryClient = useQueryClient();
    const eventSourceRef = useRef<EventSource | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
    const retryCountRef = useRef(0);
    const [isConnected, setIsConnected] = useState(false);

    const connect = useCallback(() => {
        // Only run in browser
        if (typeof window === 'undefined') return;
        if (!enabled) return;

        // Check if we've exceeded max retries
        if (retryCountRef.current >= maxRetries) {
            console.warn(`[SSE] Max retries (${maxRetries}) exceeded - stopping reconnection`);
            return;
        }

        // Close existing connection
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        console.log('[SSE] Connecting...');
        // Added withCredentials: true to ensure cookies are sent
        const eventSource = new EventSource('/api/events', { withCredentials: true });
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            console.log('[SSE] Connected');
            retryCountRef.current = 0;
            setIsConnected(true);
            onConnect?.();
        };

        eventSource.onmessage = (event) => {
            try {
                const data: SSEEvent = JSON.parse(event.data);

                switch (data.type) {
                    case 'connected':
                        console.log('[SSE] Session established');
                        break;
                    case 'invalidate':
                        if (data.queryKeys) {
                            data.queryKeys.forEach(key => {
                                queryClient.invalidateQueries({ queryKey: [key] });
                                console.log(`[SSE] Invalidated: ${key}`);
                            });
                        }
                        break;
                    case 'alert':
                        queryClient.invalidateQueries({ queryKey: ['alertas-unread'] });
                        console.log('[SSE] New alert received');
                        break;
                }
            } catch {
                // Ignore parse errors (ping messages)
            }
        };

        eventSource.onerror = (e) => {
            // Log less verbosely
            console.warn('[SSE] Connection lost');
            eventSource.close();
            setIsConnected(false);
            onError?.(new Event('error'));

            retryCountRef.current++;

            if (retryCountRef.current < maxRetries) {
                // Exponential backoff: 5s, 10s, 15s
                const delay = 5000 * retryCountRef.current;
                console.log(`[SSE] Reconnecting in ${delay / 1000}s...`);
                reconnectTimeoutRef.current = setTimeout(connect, delay);
            } else {
                console.error('[SSE] Connection failed after max retries. Refresh to try again.');
            }
        };
    }, [enabled, queryClient, onConnect, onError, maxRetries]);

    useEffect(() => {
        if (enabled) {
            retryCountRef.current = 0;
        }
    }, [enabled]);

    useEffect(() => {
        if (typeof window === 'undefined') return;

        connect();

        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connect]);

    return { isConnected };
}
