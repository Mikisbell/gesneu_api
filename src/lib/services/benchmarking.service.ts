
import { prisma } from '@/lib/prisma';
import { EstadoNeumaticoEnum } from '@prisma/client';

export interface BrandPerformance {
    marca: string;
    total_neumaticos: number;
    km_promedio_retiro: number;
    cpk_promedio: number;
    indice_reencauchabilidad: number; // 0.0 a 1.0
    costo_total_flota: number;
    modelos: ModelPerformance[];
}

export interface ModelPerformance {
    modelo: string;
    total_neumaticos: number;
    km_promedio_retiro: number;
    cpk_promedio: number;
}

export class BenchmarkingService {
    /**
     * Obtiene rendimiento agrupado por Marca (Fabricante)
     * Utiliza neumáticos DESECHADOS/VENDIDOS para datos "finales" y reales.
     */
    static async getBrandPerformance(empresaId: string): Promise<BrandPerformance[]> {
        // Obtenemos todos los neumáticos terminados que tengan datos financieros
        const neumaticosCerrados = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
                estado_actual: {
                    in: ['DESECHADO', 'VENDIDO']
                },
                kilometraje_acumulado: { gt: 0 } // Solo con uso real
            },
            include: {
                modelo: {
                    include: {
                        fabricante: true
                    }
                },
                eventos: {
                    where: { costo_evento: { not: null } }
                }
            }
        });

        // Agrupar por Marca
        const groups = new Map<string, typeof neumaticosCerrados>();

        neumaticosCerrados.forEach(n => {
            const marca = n.modelo.fabricante.nombre;
            if (!groups.has(marca)) groups.set(marca, []);
            groups.get(marca)!.push(n);
        });

        const results: BrandPerformance[] = [];

        groups.forEach((neumaticos, marca) => {
            let totalKm = 0;
            let totalCosto = 0;
            let totalReencauches = 0;
            const count = neumaticos.length;

            // Stats por modelo dentro de la marca
            const modelGroups = new Map<string, typeof neumaticosCerrados>();

            neumaticos.forEach(n => {
                const km = Number(n.kilometraje_acumulado);
                const costoCompra = Number(n.costo_compra) || 0;
                const costoEventos = n.eventos.reduce((acc, e) => acc + (Number(e.costo_evento) || 0), 0);
                const tco = costoCompra + costoEventos;

                totalKm += km;
                totalCosto += tco;
                totalReencauches += n.reencauches_realizados;

                // Agrupar modelo
                const modeloNombre = n.modelo.nombre_modelo;
                if (!modelGroups.has(modeloNombre)) modelGroups.set(modeloNombre, []);
                modelGroups.get(modeloNombre)!.push(n);
            });

            // Calcular métricas de modelos
            const modelosMetrics: ModelPerformance[] = [];
            modelGroups.forEach((nModels, modelName) => {
                let mKm = 0;
                let mCosto = 0;
                nModels.forEach(n => {
                    mKm += Number(n.kilometraje_acumulado);
                    mCosto += (Number(n.costo_compra) || 0) + n.eventos.reduce((s, e) => s + (Number(e.costo_evento) || 0), 0);
                });

                const avgKm = mKm / nModels.length;
                const avgCosto = mCosto / nModels.length;
                const avgCpk = avgKm > 0 ? (avgCosto / avgKm) : 0;

                modelosMetrics.push({
                    modelo: modelName,
                    total_neumaticos: nModels.length,
                    km_promedio_retiro: Math.round(avgKm),
                    cpk_promedio: Number(avgCpk.toFixed(4))
                });
            });

            // Métricas Globales Marca
            const kmPromedio = totalKm / count;
            const costoPromedio = totalCosto / count;
            const cpkPromedio = kmPromedio > 0 ? (costoPromedio / kmPromedio) : 0;

            // Indice Reencauchabilidad: (Total Reencauches / Total Neumaticos Retirados)
            // Ejemplo: si 10 llantas se retiraron y en total tuvieron 5 reencauches, índice 0.5
            // O mejor: % de carcasas que aceptaron al menos 1 reencauche.
            // Usaremos promedio de reencauches por llanta para simplificar.
            const indiceReencauchabilidad = totalReencauches / count;

            results.push({
                marca,
                total_neumaticos: count,
                km_promedio_retiro: Math.round(kmPromedio),
                cpk_promedio: Number(cpkPromedio.toFixed(4)),
                indice_reencauchabilidad: Number(indiceReencauchabilidad.toFixed(2)),
                costo_total_flota: totalCosto,
                modelos: modelosMetrics.sort((a, b) => a.cpk_promedio - b.cpk_promedio)
            });
        });

        // Ordenar marcas por CPK ascendente (Mejor rendimiento primero)
        return results.sort((a, b) => a.cpk_promedio - b.cpk_promedio);
    }
}
