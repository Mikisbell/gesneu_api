import { prisma } from '@/lib/prisma';
import {
    EstadoNeumaticoEnum,
    TipoEventoNeumaticoEnum
} from '@prisma/client';
import { NeumaticoService } from './neumatico.service';
import { unstable_cache, revalidateTag } from 'next/cache';
import { EventBus } from '../events/core';
import { ReencaucheEvents } from '../events/reencauche.events';
import { registerObservers } from '../events/registry';

const safeRevalidateTag = (tag: string) => {
    // @ts-ignore
    try { revalidateTag(tag); } catch (e: any) { }
};

export class ReencaucheService {
    private neumaticoService = new NeumaticoService();

    constructor() {
        registerObservers();
    }

    /**
     * Envía un neumático a planta de reencauche.
     */
    async registrarEnvio(
        neumaticoId: string,
        proveedorId: string,
        usuarioId: string,
        empresaId: string
    ) {
        // 1. Validar elegibilidad
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId, empresa_id: empresaId }
        });

        if (!neumatico) throw new Error("Neumático no encontrado");

        // Regla: Solo si está en Almacén o Desmontado
        const estadosValidos: EstadoNeumaticoEnum[] = [
            EstadoNeumaticoEnum.EN_STOCK,
            // EstadoNeumaticoEnum.PARA_REENCAUCHE // Removed if invalid, or mapped to EN_STOCK with condition
        ];

        if (!estadosValidos.includes(neumatico.estado_actual)) {
            throw new Error(`Estado inválido para envío: ${neumatico.estado_actual}`);
        }

        // 2. Registrar Evento y Actualizar Estado
        const result = await this.neumaticoService.registrarEvento({
            tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA,
            neumatico_id: neumaticoId,
            proveedor_id: proveedorId,
            fecha_evento: new Date().toISOString(),
            costo_evento: 0, // Costo se registra al retorno o facturación
            // notas: "Envío a planta de reencauche" // Removed as it is not in type definition
        }, usuarioId, empresaId);

        // Emit Event (Architecture 2026: Decoupled Side Effects)
        await EventBus.publish(ReencaucheEvents.SENT, {
            neumaticoId,
            empresaId,
            usuarioId
        });

        return result;
    }

    /**
     * Procesa el retorno de un neumático reencauchado (¡El momento crítico!)
     */
    async registrarRetorno(
        neumaticoId: string,
        datosRetorno: {
            profundidad_nueva: number;
            proveedor_id: string; // Quien lo reencauchó
            costo: number;
            diseno_banda?: string; // Nuevo dibujo?
            almacen_destino_id: string;
        },
        usuarioId: string,
        empresaId: string
    ) {
        // 1. Validar
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId, empresa_id: empresaId }
        });

        if (!neumatico) throw new Error("Neumático no encontrado");

        // 2. Calcular nuevos contadores
        const nuevaVida = (neumatico.vida_actual || 1) + 1;
        const nuevosReencauches = (neumatico.reencauches_realizados || 0) + 1;

        // 3. Ejecutar Transacción de Actualización
        // Usamos prisma directo para updates específicos que el servicio genérico podría no manejar
        const result = await prisma.$transaction(async (tx) => {

            // A. Actualizar Neumático (Atomic Check: Must be EN_REENCAUCHE)
            const updatedTire = await tx.neumatico.update({
                where: {
                    id: neumaticoId,
                    // Optimistic Concurrency Control: Only update if still in REENCAUCHE
                    // This prevents double-processing if parallel requests hit
                    estado_actual: EstadoNeumaticoEnum.EN_REENCAUCHE
                },
                data: {
                    estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                    ubicacion_almacen_id: datosRetorno.almacen_destino_id,
                    ubicacion_vehiculo_id: null,
                    ubicacion_posicion_id: null,

                    // Lógica de Ciclo de Vida
                    es_reencauchado: true,
                    vida_actual: nuevaVida,
                    reencauches_realizados: nuevosReencauches,
                    fecha_ultimo_reencauche: new Date(),

                    // Reset de Métricas para la Nueva Vida
                    kilometraje_vida_actual: 0,
                    profundidad_remanente_actual_mm: datosRetorno.profundidad_nueva,
                    profundidad_inicio_vida_actual_mm: datosRetorno.profundidad_nueva, // ¡Importante para desgaste!

                    actualizado_por: usuarioId,
                    actualizado_en: new Date()
                }
            });

            // B. Registrar Evento
            return await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
                    neumatico_id: neumaticoId,
                    fecha_evento: new Date(),
                    proveedor_id: datosRetorno.proveedor_id,
                    almacen_destino_id: datosRetorno.almacen_destino_id,
                    costo_evento: datosRetorno.costo,

                    // Snapshot de estado
                    profundidad_remanente: datosRetorno.profundidad_nueva,

                    notas: `Retorno de Reencauche #${nuevosReencauches}. Vida ${nuevaVida} iniciada.`,
                    creado_por: usuarioId
                }
            });
        });

        // Emit Event (Decoupled Side Effects)
        await EventBus.publish(ReencaucheEvents.RETURNED, {
            neumaticoId,
            empresaId,
            nuevoReencaucheCount: nuevosReencauches,
            nuevaProfundidad: datosRetorno.profundidad_nueva
        });

        return result;
    }

    /**
     * Calcula el Índice de Reencauchabilidad (IR)
     * Fórmula: Sum(Cant * N_Reencauches) / Total
     * CACHED: Cacheado por 1 minuto o hasta invalidación.
     */
    async getIndiceReencauchabilidad(empresaId: string) {
        // 2026 Technique: unstable_cache (Native Next.js Server Cache)
        const getCachedIndice = unstable_cache(
            async (id: string) => {
                const neumaticos = await prisma.neumatico.findMany({
                    where: {
                        empresa_id: id,
                        estado_actual: { not: EstadoNeumaticoEnum.DESECHADO }
                    },
                    select: {
                        id: true,
                        reencauches_realizados: true,
                    }
                });

                if (neumaticos.length === 0) return { ir_global: 0, breakdown: [] };

                let sumaPonderada = 0;
                neumaticos.forEach(n => { sumaPonderada += (n.reencauches_realizados || 0); });

                const irGlobal = Number((sumaPonderada / neumaticos.length).toFixed(2));

                return {
                    total_neumaticos: neumaticos.length,
                    total_vidas_acumuladas: sumaPonderada,
                    ir_global: irGlobal,
                    interpretacion: irGlobal < 1 ? "Flota Mayormente Nueva" : "Flota Madura/Optimizada"
                };
            },
            [`reencauche-indice-${empresaId}`],
            {
                revalidate: 60, // 60 seconds TTL (Stale-While-Revalidate)
                tags: [`reencauche-metrics-${empresaId}`]
            }
        );

        return await getCachedIndice(empresaId);
    }
}
