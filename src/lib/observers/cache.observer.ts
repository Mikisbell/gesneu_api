import { EventBus, DomainEvent } from '../events/core';
import { ReencaucheEvents, ReencaucheReturnedPayload, ReencaucheSentPayload } from '../events/reencauche.events';
import { revalidateTag } from 'next/cache';

// Helper for safe revalidation
const safeRevalidateTag = (tag: string) => {
    // @ts-ignore
    try { revalidateTag(tag); } catch (e: any) { }
};

export class CacheObserver {
    static init() {
        console.log("🔌 [Observer] Initializing Cache Strategies...");

        // On Sent -> Invalidate Index
        EventBus.subscribe<ReencaucheSentPayload>(ReencaucheEvents.SENT, async (event) => {
            console.log(`🧹 [Cache] Invalidating metrics for ${event.payload.empresaId} (Event: SENT)`);
            safeRevalidateTag(`reencauche-metrics-${event.payload.empresaId}`);
        });

        // On Returned -> Invalidate Index
        EventBus.subscribe<ReencaucheReturnedPayload>(ReencaucheEvents.RETURNED, async (event) => {
            console.log(`🧹 [Cache] Invalidating metrics for ${event.payload.empresaId} (Event: RETURNED)`);
            safeRevalidateTag(`reencauche-metrics-${event.payload.empresaId}`);
        });
    }
}
