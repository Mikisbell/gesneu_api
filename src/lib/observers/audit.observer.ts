import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents } from '../events/neumatico.events';
import type {
    TirePurchasedPayload,
    TireMountedPayload,
    TireDismountedPayload,
    TireRotatedPayload,
    TireScrappedPayload,
    RepairStartedPayload,
    RepairCompletedPayload,
    RetreadSentPayload,
    RetreadReturnedPayload
} from '../events/neumatico.events';
import { prisma } from '@/lib/prisma';

/**
 * AuditObserver
 *
 * Responsibilities:
 * - Log ALL tire operation events to console for debugging
 * - Persist to auditoria_log table for compliance and audit trail
 * - Future: Stream to external analytics platforms (Mixpanel, Amplitude)
 *
 * Design Principle: Read-only observer. Never modifies data.
 * DB write failures are caught and logged to prevent breaking the main operation.
 */
export class AuditObserver {
    static init() {
        console.log("📝 [Observer] Initializing Audit System...");

        // Subscribe to all tire lifecycle events
        EventBus.subscribe<TirePurchasedPayload>(NeumaticoEvents.PURCHASED, this.logEvent);
        EventBus.subscribe<TireMountedPayload>(NeumaticoEvents.MOUNTED, this.logEvent);
        EventBus.subscribe<TireDismountedPayload>(NeumaticoEvents.DISMOUNTED, this.logEvent);
        EventBus.subscribe<TireRotatedPayload>(NeumaticoEvents.ROTATED, this.logEvent);
        EventBus.subscribe<TireScrappedPayload>(NeumaticoEvents.SCRAPPED, this.logEvent);

        // Subscribe to repair cycle events
        EventBus.subscribe<RepairStartedPayload>(NeumaticoEvents.REPAIR_STARTED, this.logEvent);
        EventBus.subscribe<RepairCompletedPayload>(NeumaticoEvents.REPAIR_COMPLETED, this.logEvent);

        // Subscribe to retread cycle events
        EventBus.subscribe<RetreadSentPayload>(NeumaticoEvents.RETREAD_SENT, this.logEvent);
        EventBus.subscribe<RetreadReturnedPayload>(NeumaticoEvents.RETREAD_RETURNED, this.logEvent);

        console.log("✅ [AuditObserver] Subscribed to 9 event types");
    }

    /**
     * Universal event logger
     * Persists to database AND logs to console for development
     * Safe: All exceptions are caught to prevent observer failures from breaking system
     */
    private static async logEvent(event: DomainEvent<any>) {
        try {
            const { name: type, payload, timestamp } = event;

            // Structured logging for production monitoring
            console.log(`📋 [AUDIT] ${type}`, {
                eventType: type,
                neumaticoId: payload.neumaticoId,
                empresaId: payload.empresaId,
                usuarioId: payload.usuarioId,
                timestamp: timestamp.toISOString(),
                metadata: payload.metadata,
                // Include specific fields based on event type
                ...(payload.vehiculoId && { vehiculoId: payload.vehiculoId }),
                ...(payload.proveedorId && { proveedorId: payload.proveedorId }),
                ...(payload.motivoTexto && { motivoTexto: payload.motivoTexto })
            });

            // Persist to database (fire-and-forget, errors caught below)
            await prisma.auditoriaLog.create({
                data: {
                    esquema_tabla: 'public',
                    nombre_tabla: 'neumaticos',
                    operacion: this.mapEventTypeToOperation(type),
                    usuario_app_id: payload.usuarioId ?? null,
                    usuario_app: payload.usuarioId ?? null,
                    entidad_id: payload.neumaticoId ?? null,
                    datos_antiguos: payload.datosAntiguos ?? null,
                    datos_nuevos: payload.datosNuevos ?? null,
                    cambios: payload.cambios ?? payload.metadata ?? null,
                }
            });

            // TODO: Phase 3 - Send to external analytics
            // await analytics.track(payload.usuarioId, type, payload);

        } catch (error: any) {
            // Observer failures should NEVER break the main system
            console.error(`❌ [AuditObserver] Failed to log event: ${error.message}`);
        }
    }

    /**
     * Map event type names to audit operation types
     */
    private static mapEventTypeToOperation(eventType: string): string {
        const lower = eventType.toLowerCase();
        if (lower.includes('purchase') || lower.includes('compra')) return 'INSERT';
        if (lower.includes('scrap') || lower.includes('desecho') || lower.includes('delete')) return 'DELETE';
        return 'UPDATE';
    }
}
