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
}
