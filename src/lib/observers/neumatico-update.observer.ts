import { prisma } from '@/lib/prisma';
import { EventBus } from '../events/core';
import { InspeccionEvents, PressureReadPayload, DepthReadPayload } from '../events/inspeccion.events';

export class NeumaticoUpdateObserver {
    static init() {
        console.log("💾 [Observer] Initializing State Sync...");

        // SYNC PRESSURE
        EventBus.subscribe<PressureReadPayload>(InspeccionEvents.PRESSURE_READ, async (event) => {
            await prisma.neumatico.update({
                where: { id: event.payload.neumaticoId },
                data: {
                    presion_actual_psi: event.payload.presionPsi,
                    actualizado_en: new Date()
                }
            });
        });

        // SYNC DEPTH & ODOMETER
        EventBus.subscribe<DepthReadPayload>(InspeccionEvents.DEPTH_READ, async (event) => {
            const updateData: any = {
                profundidad_remanente_actual_mm: event.payload.profundidadPromedio,
                profundidad_int: event.payload.profunidades.int,
                profundidad_cen: event.payload.profunidades.cen,
                profundidad_ext: event.payload.profunidades.ext,
                fecha_ultima_medicion_profundidad: new Date(),
                actualizado_en: new Date()
            };

            // Update KM if provided
            if (event.payload.kilometraje) {
                // Warning: This ignores KM delta logic (keeping it simple for now)
                updateData.kilometraje_acumulado = event.payload.kilometraje;
            }

            await prisma.neumatico.update({
                where: { id: event.payload.neumaticoId },
                data: updateData
            });
        });
    }
}
