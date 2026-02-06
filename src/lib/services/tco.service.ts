import { prisma } from '@/lib/prisma';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

// Factores de estimación (configurables)
const FACTOR_PENALIDAD_COMBUSTIBLE_POR_PSI = 0.003; // 0.3% extra fuel per PSI missing
const ESTIMADO_CONSUMO_GALON_KM = 0.15; // ~6.6 km/galón (camión pesado)
const COSTO_GALON_USD = 4.5;

export interface FinancialMetrics {
    tco: number;
    cpk: number;
    cpk_projected: number;
    costo_compra: number;
    costo_mantenimiento: number;
    fuel_waste_estimated_usd: number;
    currency: string;
}

export class TcoService {
    /**
     * Calcula métricas financieras completas para un neumático
     */
    static async getFinancials(neumaticoId: string): Promise<FinancialMetrics> {
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId },
            include: {
                modelo: true,
                eventos: {
                    where: {
                        costo_evento: { not: null }
                    },
                    select: {
                        tipo_evento: true,
                        costo_evento: true,
                        fecha_evento: true
                    }
                },
                lecturas_presion: {
                    orderBy: { fecha_lectura: 'desc' },
                    take: 50 // Usar últimas 50 para estimación reciente
                },
                inspecciones: {
                    orderBy: { creado_en: 'desc' },
                    take: 50
                }
            }
        });

        if (!neumatico) {
            throw new Error(`Neumatico ${neumaticoId} not found`);
        }

        // 1. Costos Directos
        const costoCompra = Number(neumatico.costo_compra) || 0;

        const costoMantenimiento = neumatico.eventos.reduce((total, evento) => {
            // Filtrar tipos si es necesario, pero asumimos que todo costo asignado suma al TCO
            return total + (Number(evento.costo_evento) || 0);
        }, 0);

        const tco = costoCompra + costoMantenimiento;

        // 2. CPK
        const kmAcumulados = Number(neumatico.kilometraje_acumulado) || 0;
        const cpk = kmAcumulados > 0 ? (tco / kmAcumulados) : 0;

        // 3. CPK Proyectado
        // TCO / (KmActuales + KmRestantesEstimados)
        // Usamos vida_util_restante_km si existe, o estimamos simple
        const kmRestantes = Number(neumatico.vida_util_restante_km) || 0;
        const cpkProjected = (kmAcumulados + kmRestantes) > 0
            ? (tco / (kmAcumulados + kmRestantes))
            : 0;

        // 4. Impacto Combustible (Estimado)
        // Basado en lecturas de presión vs recomendación
        const presionIdeal = Number(neumatico.modelo.presion_recomendada_psi) || 100; // Default 100
        let fuelPenaltyTotal = 0;

        // Unificar lecturas de ambas fuentes
        const lecturas = [
            ...neumatico.lecturas_presion.map(l => ({ psi: Number(l.presion_psi), fecha: l.fecha_lectura })),
            ...neumatico.inspecciones.map(i => ({ psi: Number(i.psi_medido), fecha: i.creado_en }))
        ];

        if (lecturas.length > 0) {
            // Promedio de desviación
            let totalDeviationPct = 0;
            let count = 0;

            lecturas.forEach(l => {
                if (l.psi < presionIdeal) {
                    const deficit = presionIdeal - l.psi;
                    totalDeviationPct += (deficit / presionIdeal); // % faltante
                    count++;
                }
            });

            if (count > 0) {
                const avgDeficitPct = totalDeviationPct / count;
                // Si falta 10%, penalidad = 10 (psi aprox) * 0.3% = 3% extra fuel
                // Fórmula simple: avgDeficitPsi * FACTOR
                // Deficit Promedio en PSI = avgDeficitPct * presionIdeal
                const avgDeficitPsi = avgDeficitPct * presionIdeal;
                const extraFuelPct = avgDeficitPsi * FACTOR_PENALIDAD_COMBUSTIBLE_POR_PSI;

                // Costo Combustible Estimado durante el recorrido
                // Asumimos que este déficit aplicó a todo el kilometraje (simplificación)
                // FuelUsed = Km * Galon/Km
                // Wasted = FuelUsed * extraFuelPct * CostoGalon
                const totalFuel = kmAcumulados * ESTIMADO_CONSUMO_GALON_KM;
                fuelPenaltyTotal = totalFuel * extraFuelPct * COSTO_GALON_USD;
            }
        }

        return {
            tco,
            cpk,
            cpk_projected: cpkProjected,
            costo_compra: costoCompra,
            costo_mantenimiento: costoMantenimiento,
            fuel_waste_estimated_usd: fuelPenaltyTotal,
            currency: neumatico.moneda_compra || 'USD'
        };
    }
}
