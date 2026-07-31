import { prisma } from '@/lib/prisma';
import { EventBus } from '../events/core';
import { InspeccionEvents, PressureReadPayload, DepthReadPayload } from '../events/inspeccion.events';
import { TipoAlertaEnum, SeveridadAlertaEnum, WebhookEventType } from '@prisma/client';

export class AlertObserver {
    static init() {
        console.log("🚨 [Observer] Initializing Alert Systems...");

        // PRESSURE MONITOR
        EventBus.subscribe<PressureReadPayload>(InspeccionEvents.PRESSURE_READ, async (event) => {
            const { neumaticoId, presionPsi, empresaId } = event.payload;

            // 1. Get Tire Specs
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: neumaticoId },
                include: { modelo: true }
            });

            if (!neumatico || !neumatico.modelo.presion_recomendada_psi) return;

            const recommended = Number(neumatico.modelo.presion_recomendada_psi);
            const criticalThreshold = recommended * 0.8; // < 80% → CRITICAL
            const warningThreshold  = recommended * 0.9; // < 90% → WARNING

            let severidad: SeveridadAlertaEnum | null = null;
            if (presionPsi < criticalThreshold) {
                severidad = SeveridadAlertaEnum.CRITICAL;
            } else if (presionPsi < warningThreshold) {
                severidad = SeveridadAlertaEnum.WARNING;
            }

            if (!severidad) return; // presión dentro de rango → no alerta

            console.log(`⚠️ [Alert] ${severidad} Pressure on ${neumatico.numero_serie}: ${presionPsi} PSI / recommended ${recommended} PSI`);

            // 2. Create Alert (Idempotent: skip if unresolved alert already exists)
            const existing = await prisma.alerta.findFirst({
                where: {
                    neumatico_id: neumaticoId,
                    tipo: TipoAlertaEnum.PRESION_BAJA,
                    resuelta: false
                }
            });

            if (existing) return;

            const alerta = await prisma.alerta.create({
                data: {
                    tipo: TipoAlertaEnum.PRESION_BAJA,
                    severidad,
                    neumatico_id: neumaticoId,
                    mensaje: `Presión ${severidad === SeveridadAlertaEnum.CRITICAL ? 'CRÍTICA' : 'baja'}: ${presionPsi} PSI (Recomendado: ${recommended})`,
                    leida: false
                }
            });

            // 3. Dispatch webhook for CRITICAL alerts
            if (severidad === SeveridadAlertaEnum.CRITICAL && empresaId) {
                try {
                    const { WebhookService } = require('../services/webhook.service');
                    const webhookService = new WebhookService();
                    await webhookService.dispatch(
                        WebhookEventType.ALERTA_CRITICAL,
                        {
                            ...alerta,
                            neumatico: { numero_serie: neumatico.numero_serie }
                        },
                        empresaId
                    );
                } catch (err) {
                    console.error('[AlertObserver] Webhook dispatch failed:', err);
                }
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
