/**
 * SSE Event Emitter Service
 * 
 * This service manages Server-Sent Events connections and broadcasts
 * events to connected clients when data changes.
 * 
 * Usage from other services:
 * ```typescript
 * import { sseEmitter } from '@/lib/services/sse-emitter.service';
 * 
 * // After creating/updating data:
 * sseEmitter.broadcast({
 *   type: 'invalidate',
 *   queryKeys: ['neumaticos', 'alertas-unread']
 * });
 * ```
 */

type SSEClient = {
    id: string;
    userId: string;
    controller: ReadableStreamDefaultController<Uint8Array>;
    empresaId: string;
};

interface SSEBroadcastEvent {
    type: 'invalidate' | 'alert' | 'update';
    queryKeys?: string[];
    data?: any;
    targetUserId?: string;      // Send to specific user
    targetEmpresaId?: string;   // Send to all users of an empresa
}

class SSEEmitterService {
    private clients: Map<string, SSEClient> = new Map();
    private encoder = new TextEncoder();

    /**
     * Register a new SSE client
     */
    addClient(client: SSEClient): void {
        this.clients.set(client.id, client);
        console.log(`[SSE] Client connected: ${client.id} (Total: ${this.clients.size})`);
    }

    /**
     * Remove a client when they disconnect
     */
    removeClient(clientId: string): void {
        this.clients.delete(clientId);
        console.log(`[SSE] Client disconnected: ${clientId} (Total: ${this.clients.size})`);
    }

    /**
     * Broadcast an event to all connected clients
     * Optionally filter by userId or empresaId
     */
    broadcast(event: SSEBroadcastEvent): void {
        const payload = JSON.stringify({
            ...event,
            timestamp: Date.now(),
        });
        const message = this.encoder.encode(`data: ${payload}\n\n`);

        this.clients.forEach((client, id) => {
            try {
                // Filter by target if specified
                if (event.targetUserId && client.userId !== event.targetUserId) {
                    return;
                }
                if (event.targetEmpresaId && client.empresaId !== event.targetEmpresaId) {
                    return;
                }

                client.controller.enqueue(message);
            } catch (error) {
                console.error(`[SSE] Failed to send to client ${id}:`, error);
                this.removeClient(id);
            }
        });

        console.log(`[SSE] Broadcast: ${event.type} to ${this.clients.size} clients`);
    }

    /**
     * Notify clients that alerts have been updated
     */
    notifyAlertsUpdate(empresaId: string): void {
        this.broadcast({
            type: 'invalidate',
            queryKeys: ['alertas-unread', 'alertas'],
            targetEmpresaId: empresaId,
        });
    }

    /**
     * Notify clients that neumaticos have been updated
     */
    notifyNeumaticosUpdate(empresaId: string): void {
        this.broadcast({
            type: 'invalidate',
            queryKeys: ['neumaticos'],
            targetEmpresaId: empresaId,
        });
    }

    /**
     * Notify clients that vehiculos have been updated
     */
    notifyVehiculosUpdate(empresaId: string): void {
        this.broadcast({
            type: 'invalidate',
            queryKeys: ['vehiculos'],
            targetEmpresaId: empresaId,
        });
    }

    /**
     * Get number of connected clients
     */
    getClientCount(): number {
        return this.clients.size;
    }
}

// Singleton instance
export const sseEmitter = new SSEEmitterService();
