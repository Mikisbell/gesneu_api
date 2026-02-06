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

/**
 * AuditObserver
 * 
 * Responsibilities:
 * - Log ALL tire operation events to console for debugging
 * - Future: Persist to audit_log table for compliance
 * - Future: Stream to external analytics platforms (Mixpanel, Amplitude)
 * 
 * Design Principle: Read-only observer. Never modifies data.
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

            // TODO: Phase 2 - Persist to database
            // await prisma.auditLog.create({
            //     data: {
            //         evento_tipo: type,
            //         entidad_tipo: 'NEUMATICO',
            //         entidad_id: payload.neumaticoId,
            //         empresa_id: payload.empresaId,
            //         usuario_id: payload.usuarioId,
            //         metadata: payload,
            //         timestamp: timestamp
            //     }
            // });

            // TODO: Phase 3 - Send to external analytics
            // await analytics.track(payload.usuarioId, type, payload);

        } catch (error: any) {
            // Observer failures should NEVER break the main system
            console.error(`❌ [AuditObserver] Failed to log event: ${error.message}`);
        }
    }
}
