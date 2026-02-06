import { prisma } from '@/lib/prisma';
import { EventBus } from '../events/core';
import { InspeccionEvents, PressureReadPayload, DepthReadPayload } from '../events/inspeccion.events';
import { TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';

export class AlertObserver {
    static init() {
        console.log("🚨 [Observer] Initializing Alert Systems...");

        // PRESSURE MONITOR
        EventBus.subscribe<PressureReadPayload>(InspeccionEvents.PRESSURE_READ, async (event) => {
            const { neumaticoId, presionPsi } = event.payload;

            // 1. Get Tire Specs
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: neumaticoId },
                include: { modelo: true }
            });

            if (!neumatico || !neumatico.modelo.presion_recomendada_psi) return;

            const recommended = Number(neumatico.modelo.presion_recomendada_psi);
            const threshold = recommended * 0.9; // 10% tolerance

            if (presionPsi < threshold) {
                console.log(`⚠️ [Alert] Low Pressure detected on ${neumatico.numero_serie}: ${presionPsi} / ${recommended}`);

                // Create Alert (Idempotent check ideal here, but simpler for now)
                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.PRESION_BAJA,
                        severidad: SeveridadAlertaEnum.WARNING,
                        neumatico_id: neumaticoId,
                        mensaje: `Presión baja: ${presionPsi} PSI (Recomendado: ${recommended})`,
                        leida: false
                    }
                });
            }
        });

        // TREAD DEPTH MONITOR
        EventBus.subscribe<DepthReadPayload>(InspeccionEvents.DEPTH_READ, async (event) => {
            const { neumaticoId, profundidadPromedio } = event.payload;

            // 1. Check Threshold (Hardcoded generic for now, ideally from Model Spec)
            const CRITICAL_DEPTH = 3.0; // mm

            if (profundidadPromedio <= CRITICAL_DEPTH) {
                console.log(`⚠️ [Alert] Critical Depth on ${neumaticoId}: ${profundidadPromedio}mm`);

                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.PROFUNDIDAD_MINIMA,
                        severidad: SeveridadAlertaEnum.CRITICAL,
                        neumatico_id: neumaticoId,
                        mensaje: `Profundidad crítica: ${profundidadPromedio.toFixed(1)}mm. Requiere cambio o reencauche.`,
                        leida: false
                    }
                });
            }
        });
    }
}
