import { prisma } from '@/lib/prisma';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

export interface CPKMetrics {
    neumatico_id: string;
    numero_serie: string;
    cpk: number;
    kilometraje_total: number;
    costo_total: number;
    desglose: {
        compra: number;
        reparaciones: number;
        reencauches: number;
        otros: number;
    };
    moneda: string;
}

export interface WearRateMetrics {
    neumatico_id: string;
    numero_serie: string;
    desgaste_mm_por_1000km: number;
    profundidad_inicial_mm: number;
    profundidad_actual_mm: number;
    desgaste_total_mm: number;
    kilometraje_total: number;
    vida_restante_estimada_km: number | null;
    estado: 'OPTIMO' | 'NORMAL' | 'CRITICO';
}

export class ReportesService {
    /**
     * Calcula el Costo Por Kilómetro (CPK) de un neumático específico.
     * CPK = (Costo Compra + Costos Mantenimiento) / Kilometraje Acumulado
     */
    async getCPK(neumaticoId: string): Promise<CPKMetrics> {
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId },
            include: {
                eventos: {
                    where: {
                        costo_evento: { not: null }
                    },
                    select: {
                        tipo_evento: true,
                        costo_evento: true
                    }
                }
            }
        });

        if (!neumatico) {
            throw new Error('Neumático no encontrado');
        }

        const costoCompra = Number(neumatico.costo_compra?.toString() ?? 0);

        let costoReparaciones = 0;
        let costoReencauches = 0;
        let costoOtros = 0;

        neumatico.eventos.forEach(evento => {
            const costo = Number(evento.costo_evento?.toString() ?? 0);

            if (evento.tipo_evento === TipoEventoNeumaticoEnum.REPARACION_SALIDA) {
                costoReparaciones += costo;
            } else if (evento.tipo_evento === TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA) {
                costoReencauches += costo;
            } else {
                costoOtros += costo; // Montajes, inspecciones costosas, etc.
            }
        });

        const costoTotal = costoCompra + costoReparaciones + costoReencauches + costoOtros;
        const kilometrajeTotal = neumatico.kilometraje_acumulado || 0;

        // Evitar división por cero
        let cpk = 0;
        if (kilometrajeTotal > 0) {
            cpk = costoTotal / kilometrajeTotal;
        }

        return {
            neumatico_id: neumatico.id,
            numero_serie: neumatico.numero_serie,
            cpk: Number(cpk.toFixed(4)), // 4 decimales para precisión en centavos
            kilometraje_total: kilometrajeTotal,
            costo_total: Number(costoTotal.toFixed(2)),
            desglose: {
                compra: costoCompra,
                reparaciones: costoReparaciones,
                reencauches: costoReencauches,
                otros: costoOtros
            },
            moneda: 'USD' // Asumimos USD por simplificación, podría ser configurable
        };
    }

    /**
     * Calcula el Desgaste Promedio de un neumático.
     * Fórmula: (profundidad_inicial - profundidad_actual) / km * 1000 = mm por cada 1000 km
     */
    async getDesgastePromedio(neumaticoId: string): Promise<WearRateMetrics> {
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId }
        });

        if (!neumatico) {
            throw new Error('Neumático no encontrado');
        }

        const profundidadInicial = neumatico.profundidad_inicial_mm || 0;
        const profundidadActual = neumatico.profundidad_actual_mm ?? profundidadInicial;
        const kilometrajeTotal = neumatico.kilometraje_acumulado || 0;

        const desgasteTotal = profundidadInicial - profundidadActual;

        // Desgaste en mm por cada 1000 km
        let desgastePor1000km = 0;
        if (kilometrajeTotal > 0) {
            desgastePor1000km = (desgasteTotal / kilometrajeTotal) * 1000;
        }

        // Estimar vida restante (profundidad mínima segura = 4mm)
        const PROFUNDIDAD_MINIMA = 4;
        const profundidadRestante = profundidadActual - PROFUNDIDAD_MINIMA;
        let vidaRestanteKm: number | null = null;

        if (desgastePor1000km > 0 && profundidadRestante > 0) {
            vidaRestanteKm = (profundidadRestante / desgastePor1000km) * 1000;
        }

        // Determinar estado
        let estado: 'OPTIMO' | 'NORMAL' | 'CRITICO' = 'NORMAL';
        if (profundidadActual <= PROFUNDIDAD_MINIMA) {
            estado = 'CRITICO';
        } else if (profundidadActual >= profundidadInicial * 0.7) {
            estado = 'OPTIMO';
        }

        return {
            neumatico_id: neumatico.id,
            numero_serie: neumatico.numero_serie,
            desgaste_mm_por_1000km: Number(desgastePor1000km.toFixed(3)),
            profundidad_inicial_mm: profundidadInicial,
            profundidad_actual_mm: profundidadActual,
            desgaste_total_mm: Number(desgasteTotal.toFixed(2)),
            kilometraje_total: kilometrajeTotal,
            vida_restante_estimada_km: vidaRestanteKm ? Math.round(vidaRestanteKm) : null,
            estado
        };
    }
}

