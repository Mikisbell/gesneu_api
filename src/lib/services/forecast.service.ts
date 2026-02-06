
import { prisma } from '@/lib/prisma';

export interface PurchaseForecastItem {
    medida: string;
    cantidad_sugerida: number;
    detalles_neumaticos: {
        serie: string;
        mm_actual: number;
        dias_restantes_estimados: number;
        fecha_proyectada_retiro: Date;
    }[];
}

export class ForecastService {
    /**
     * Genera forecast de compras para los próximos 90 días (default)
     */
    static async generatePurchaseForecast(empresaId: string, daysAhead: number = 90): Promise<PurchaseForecastItem[]> {
        const minDepth = 3; // MM de retiro estándar (ajustable por política)
        const defaultWearRate = 0.1; // MM/día default si no hay historial (conservador)

        // 1. Obtener neumáticos activos
        const activeTires = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
                estado_actual: 'EN_USO',
                profundidad_remanente_actual_mm: { gt: minDepth }
            },
            include: {
                modelo: true
            }
        });

        const reportMap = new Map<string, PurchaseForecastItem>();

        for (const tire of activeTires) {
            const currentMm = Number(tire.profundidad_remanente_actual_mm);
            // Calcular tasa desgaste (simple: (original - actual) / dias_uso)
            // Si es nuevo, usar default.

            const daysInUse = Math.max(1, (new Date().getTime() - new Date(tire.fecha_compra).getTime()) / (1000 * 3600 * 24));
            const mmLost = Number(tire.modelo.profundidad_original_mm) - currentMm;

            let wearRate = mmLost > 0 ? (mmLost / daysInUse) : defaultWearRate;
            if (wearRate <= 0) wearRate = defaultWearRate;

            const mmRemaining = currentMm - minDepth;
            const daysRemaining = Math.floor(mmRemaining / wearRate);

            // Proyectar fecha
            const projectionDate = new Date();
            projectionDate.setDate(projectionDate.getDate() + daysRemaining);

            // Filtrar si cae dentro de la ventana de forecast
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() + daysAhead);

            if (projectionDate <= cutoffDate) {
                // Agregar al reporte
                const dim = tire.modelo.medida || 'SIN_MEDIDA';

                if (!reportMap.has(dim)) {
                    reportMap.set(dim, {
                        medida: dim,
                        cantidad_sugerida: 0,
                        detalles_neumaticos: []
                    });
                }

                const entry = reportMap.get(dim)!;
                entry.cantidad_sugerida++;
                entry.detalles_neumaticos.push({
                    serie: tire.numero_serie,
                    mm_actual: currentMm,
                    dias_restantes_estimados: daysRemaining,
                    fecha_proyectada_retiro: projectionDate
                });
            }
        }

        return Array.from(reportMap.values());
    }
}
