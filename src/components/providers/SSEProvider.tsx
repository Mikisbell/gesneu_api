'use client';

import { useEventSource } from '@/lib/hooks/useEventSource';
import { useSession } from 'next-auth/react';
import { useEffect, useState, createContext, useContext } from 'react';

interface SSEContextType {
    isConnected: boolean;
}

const SSEContext = createContext<SSEContextType>({ isConnected: false });

export const useSSE = () => useContext(SSEContext);

/**
 * SSE Provider Component
 * 
 * Initializes Server-Sent Events connection only when user is fully authenticated.
 * Enables real-time updates across all dashboard pages.
 */
export function SSEProvider({ children }: { children: React.ReactNode }) {
    const { data: session, status } = useSession();
    const [shouldConnect, setShouldConnect] = useState(false);

    // Only enable SSE after session is confirmed and has user data
    useEffect(() => {
        if (status === 'authenticated' && session?.user?.id) {
            // Small delay to ensure auth cookies are set
            const timer = setTimeout(() => {
                setShouldConnect(true);
            }, 1000);
            return () => clearTimeout(timer);
        } else if (status === 'unauthenticated') {
            setShouldConnect(false);
        }
    }, [status, session]);

    const { isConnected } = useEventSource({
        enabled: shouldConnect,
        maxRetries: 3,
        onConnect: () => {
            console.log('[SSE] Real-time updates enabled');
        },
        onError: () => {
            console.warn('[SSE] Connection failed - will retry');
        },
    });

    return (
        <SSEContext.Provider value={{ isConnected }}>
            {children}
        </SSEContext.Provider>
    );
}
