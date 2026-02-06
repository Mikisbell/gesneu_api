import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents } from '../events/neumatico.events';
import type {
    TireMountedPayload,
    TireDismountedPayload,
    TireRotatedPayload,
    TireScrappedPayload
} from '../events/neumatico.events';
import { revalidateTag } from 'next/cache';

/**
 * AnalyticsObserver
 * 
 * Responsibilities:
 * - Invalidate caches when fleet composition changes
 * - Track KPIs (rotation frequency, scrap rate, etc.)
 * - Future: Update materialized views for dashboards
 * 
 * Design Principle: Performance optimization via cache management
 */
export class AnalyticsObserver {
    static init() {
        console.log("📊 [Observer] Initializing Analytics System...");

        // Invalidate fleet cache on mount/dismount
        EventBus.subscribe<TireMountedPayload>(NeumaticoEvents.MOUNTED, this.invalidateFleetCache);
        EventBus.subscribe<TireDismountedPayload>(NeumaticoEvents.DISMOUNTED, this.invalidateFleetCache);

        // Track rotation patterns
        EventBus.subscribe<TireRotatedPayload>(NeumaticoEvents.ROTATED, this.trackRotation);

        // Update scrap rate metrics
        EventBus.subscribe<TireScrappedPayload>(NeumaticoEvents.SCRAPPED, this.updateScrapMetrics);

        console.log("✅ [AnalyticsObserver] Subscribed to 4 metric-relevant event types");
    }

    /**
     * Invalidate fleet status cache when composition changes
     */
    private static async invalidateFleetCache(event: DomainEvent<TireMountedPayload | TireDismountedPayload>) {
        try {
            const { empresaId } = event.payload;

            console.log(`🔄 [Analytics] Invalidating fleet cache for empresa ${empresaId}`);

            // @ts-ignore - Library type mismatch in Next.js 16
            revalidateTag(`fleet-status-${empresaId}`);
            // @ts-ignore
            revalidateTag(`neumaticos-${empresaId}`);
            // @ts-ignore
            revalidateTag(`dashboard-${empresaId}`);

        } catch (error: any) {
            console.error(`❌ [AnalyticsObserver] invalidateFleetCache failed: ${error.message}`);
        }
    }

    /**
     * Track rotation events for pattern analysis
     */
    private static async trackRotation(event: DomainEvent<TireRotatedPayload>) {
        try {
            const { neumaticoId, empresaId, posicionOrigenId, posicionDestinoId, metadata } = event.payload;

            console.log(`🔄 [Analytics] Rotation tracked: ${metadata.numeroSerie} from ${posicionOrigenId} to ${posicionDestinoId}`);

            // TODO: Persist to analytics table
            // await prisma.rotationMetric.create({
            //     data: {
            //         neumatico_id: neumaticoId,
            //         empresa_id: empresaId,
            //         posicion_origen: posicionOrigenId,
            //         posicion_destino: posicionDestinoId,
            //         timestamp: event.timestamp
            //     }
            // });

            // Invalidate rotation-specific caches
            // @ts-ignore
            revalidateTag(`rotations-${empresaId}`);

        } catch (error: any) {
            console.error(`❌ [AnalyticsObserver] trackRotation failed: ${error.message}`);
        }
    }

    /**
     * Update scrap rate KPI when tire is scrapped
     */
    private static async updateScrapMetrics(event: DomainEvent<TireScrappedPayload>) {
        try {
            const { empresaId, metadata } = event.payload;

            console.log(`📉 [Analytics] Scrap recorded: ${metadata.numeroSerie} - ${metadata.kmTotales}km - $${metadata.costoTotal}`);

            // Calculate cost per km for this tire
            const costPerKm = metadata.kmTotales > 0
                ? metadata.costoTotal / metadata.kmTotales
                : 0;

            console.log(`💰 [Analytics] Cost efficiency: $${costPerKm.toFixed(4)}/km`);

            // TODO: Update aggregated metrics table
            // await prisma.scrapMetrics.upsert({
            //     where: { empresa_id: empresaId },
            //     update: {
            //         total_scrapped: { increment: 1 },
            //         total_cost_scrapped: { increment: metadata.costoTotal },
            //         avg_km_before_scrap: ... (recalculate)
            //     },
            //     create: { ... }
            // });

            // Invalidate dashboard caches
            // @ts-ignore
            revalidateTag(`scrap-rate-${empresaId}`);
            // @ts-ignore
            revalidateTag(`dashboard-${empresaId}`);

        } catch (error: any) {
            console.error(`❌ [AnalyticsObserver] updateScrapMetrics failed: ${error.message}`);
        }
    }
}
