import { EventBus, DomainEvent } from '../events/core';
import { NeumaticoEvents } from '../events/neumatico.events';
import type {
    TireScrappedPayload,
    RepairCompletedPayload,
    TireMountedPayload,
    TireDismountedPayload
} from '../events/neumatico.events';
import { prisma } from '@/lib/prisma';
import { TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';

/**
 * NotificationObserver
 * 
 * Responsibilities:
 * - Detect critical business events requiring human attention
 * - Create alerts for high-value scrap, premature wear, etc.
 * - Future: Send email/WhatsApp notifications
 * 
 * Design Principle: Business rule enforcement via side effects
 */
export class NotificationObserver {
    static init() {
        console.log("📢 [Observer] Initializing Notification System...");

        // Alert: High-value tire scrapped
        EventBus.subscribe<TireScrappedPayload>(NeumaticoEvents.SCRAPPED, this.alertHighValueScrap);

        // Alert: Premature tire wear (scrapped with low mileage)
        EventBus.subscribe<TireScrappedPayload>(NeumaticoEvents.SCRAPPED, this.alertPrematureWear);

        // Alert: Expensive repair completed
        EventBus.subscribe<RepairCompletedPayload>(NeumaticoEvents.REPAIR_COMPLETED, this.alertExpensiveRepair);

        // Alert: Frequent mount/dismount (possible issue with tire or position)
        EventBus.subscribe<TireDismountedPayload>(NeumaticoEvents.DISMOUNTED, this.alertFrequentDismount);

        console.log("✅ [NotificationObserver] Subscribed to 4 critical event types");
    }

    /**
     * Alert when a tire with high acquisition cost is scrapped
     */
    private static async alertHighValueScrap(event: DomainEvent<TireScrappedPayload>) {
        try {
            const { neumaticoId, empresaId, metadata } = event.payload;
            const HIGH_VALUE_THRESHOLD = 5000; // Configurable per empresa

            if (metadata.costoTotal > HIGH_VALUE_THRESHOLD) {
                console.log(`🚨 [ALERT] High-value tire scrapped: ${metadata.numeroSerie} - $${metadata.costoTotal}`);

                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.DESGASTE_IRREGULAR, // Using DESGASTE_IRREGULAR as proxy for high-value scrap
                        severidad: SeveridadAlertaEnum.WARNING,
                        neumatico_id: neumaticoId,
                        mensaje: `Neumático de alto valor desechado. Serie: ${metadata.numeroSerie}, Costo: $${metadata.costoTotal.toFixed(2)}, Motivo: ${event.payload.motivoTexto}`,
                        leida: false
                    }
                });

                // TODO: Send email to fleet manager
                // await emailService.send({
                //     to: 'fleet@company.com',
                //     subject: 'Neumático de alto valor desechado',
                //     body: `...`
                // });
            }
        } catch (error: any) {
            console.error(`❌ [NotificationObserver] alertHighValueScrap failed: ${error.message}`);
        }
    }

    /**
     * Alert when tire is scrapped with unusually low mileage (quality issue?)
     */
    private static async alertPrematureWear(event: DomainEvent<TireScrappedPayload>) {
        try {
            const { neumaticoId, metadata } = event.payload;
            const LOW_MILEAGE_THRESHOLD = 20000; // km

            if (metadata.kmTotales < LOW_MILEAGE_THRESHOLD) {
                console.log(`⚠️ [ALERT] Premature tire wear: ${metadata.numeroSerie} - ${metadata.kmTotales}km`);

                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.DESGASTE_IRREGULAR, // Premature wear is irregular wear
                        severidad: SeveridadAlertaEnum.WARNING,
                        neumatico_id: neumaticoId,
                        mensaje: `Desgaste prematuro detectado. Serie: ${metadata.numeroSerie}, Solo ${metadata.kmTotales}km recorridos antes de desecho. Modelo: ${metadata.modeloNombre}`,
                        leida: false
                    }
                });
            }
        } catch (error: any) {
            console.error(`❌ [NotificationObserver] alertPrematureWear failed: ${error.message}`);
        }
    }

    /**
     * Alert when repair cost is unusually high
     */
    private static async alertExpensiveRepair(event: DomainEvent<RepairCompletedPayload>) {
        try {
            const { neumaticoId, costoReal, metadata } = event.payload;
            const EXPENSIVE_REPAIR_THRESHOLD = 1000;

            if (costoReal > EXPENSIVE_REPAIR_THRESHOLD) {
                console.log(`💰 [ALERT] Expensive repair: ${metadata.numeroSerie} - $${costoReal}`);

                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.DESGASTE_IRREGULAR, // Using as proxy for expensive repair
                        severidad: SeveridadAlertaEnum.INFO,
                        neumatico_id: neumaticoId,
                        mensaje: `Reparación costosa completada. Serie: ${metadata.numeroSerie}, Costo: $${costoReal.toFixed(2)}`,
                        leida: false
                    }
                });
            }
        } catch (error: any) {
            console.error(`❌ [NotificationObserver] alertExpensiveRepair failed: ${error.message}`);
        }
    }

    /**
     * Alert if tire is frequently dismounted (may indicate problem)
     */
    private static async alertFrequentDismount(event: DomainEvent<TireDismountedPayload>) {
        try {
            const { neumaticoId, metadata } = event.payload;

            // Count recent DESMONTAJE events for this tire (last 30 days)
            const recentDismounts = await prisma.eventoNeumatico.count({
                where: {
                    neumatico_id: neumaticoId,
                    tipo_evento: 'DESMONTAJE',
                    fecha_evento: {
                        gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
                    }
                }
            });

            if (recentDismounts >= 3) {
                console.log(`🔄 [ALERT] Frequent dismount: ${metadata.numeroSerie} - ${recentDismounts} times in 30 days`);

                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.DESGASTE_IRREGULAR, // Frequent dismount indicates problem
                        severidad: SeveridadAlertaEnum.INFO,
                        neumatico_id: neumaticoId,
                        mensaje: `Desmontaje frecuente detectado. Serie: ${metadata.numeroSerie}, ${recentDismounts} desmontajes en 30 días. Requiere investigación.`,
                        leida: false
                    }
                });
            }
        } catch (error: any) {
            console.error(`❌ [NotificationObserver] alertFrequentDismount failed: ${error.message}`);
        }
    }
}
