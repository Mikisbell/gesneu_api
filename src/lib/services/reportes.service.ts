import { prisma } from '@/lib/prisma';
import { TipoEventoNeumaticoEnum } from '@prisma/client';
import { toNumber } from '@/lib/utils/decimal';

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
    profundidad_remanente_actual_mm: number;
    desgaste_total_mm: number;
    kilometraje_total: number;
    vida_restante_estimada_km: number | null;
    estado: 'OPTIMO' | 'NORMAL' | 'CRITICO';
}

export interface BrandCPKStats {
    fabricante_id: string;
    fabricante_nombre: string;
    cpk_promedio: number;
    cpk_minimo: number;
    cpk_maximo: number;
    total_neumaticos: number;
    kilometraje_total: number;
    costo_total: number;
}

export interface BrandComparisonResult {
    marcas: BrandCPKStats[];
    mejor_marca: string | null;
    peor_marca: string | null;
    fecha_calculo: string;
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
        const kilometrajeTotal = toNumber(neumatico.kilometraje_acumulado);

        // Evitar división por cero
        let cpk = 0;
        if (kilometrajeTotal > 0) {
            cpk = costoTotal / kilometrajeTotal;
        }

        return {
            neumatico_id: neumatico.id,
            numero_serie: neumatico.numero_serie || 'S/N',
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

        const profundidadInicial = toNumber(neumatico.profundidad_inicial_mm);
        const profundidadActual = toNumber(neumatico.profundidad_remanente_actual_mm, profundidadInicial);
        const kilometrajeTotal = toNumber(neumatico.kilometraje_acumulado);

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
            numero_serie: neumatico.numero_serie || 'S/N',
            desgaste_mm_por_1000km: Number(desgastePor1000km.toFixed(3)),
            profundidad_inicial_mm: profundidadInicial,
            profundidad_remanente_actual_mm: profundidadActual,
            desgaste_total_mm: Number(desgasteTotal.toFixed(2)),
            kilometraje_total: kilometrajeTotal,
            vida_restante_estimada_km: vidaRestanteKm ? Math.round(vidaRestanteKm) : null,
            estado
        };
    }

    /**
     * Compara el CPK promedio entre diferentes fabricantes/marcas.
     * Agrupa todos los neumáticos con kilometraje > 0 por fabricante.
     */
    async getComparativoMarcas(): Promise<BrandComparisonResult> {
        // Obtener todos los neumáticos con km > 0 y sus fabricantes
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                kilometraje_acumulado: { gt: 0 }
            },
            include: {
                modelo: {
                    include: {
                        fabricante: true
                    }
                },
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

        // Agrupar por fabricante
        const fabricantesMap = new Map<string, {
            id: string;
            nombre: string;
            cpks: number[];
            kmTotal: number;
            costoTotal: number;
        }>();

        for (const n of neumaticos) {
            const fabricante = n.modelo.fabricante;
            if (!fabricante) continue;

            // Calcular CPK individual
            const costoCompra = Number(n.costo_compra?.toString() ?? 0);
            let costoEventos = 0;
            n.eventos.forEach(e => {
                costoEventos += Number(e.costo_evento?.toString() ?? 0);
            });
            const costoTotal = costoCompra + costoEventos;
            const km = toNumber(n.kilometraje_acumulado);
            const cpk = km > 0 ? costoTotal / km : 0;

            // Agregar a mapa
            if (!fabricantesMap.has(fabricante.id)) {
                fabricantesMap.set(fabricante.id, {
                    id: fabricante.id,
                    nombre: fabricante.nombre,
                    cpks: [],
                    kmTotal: 0,
                    costoTotal: 0
                });
            }

            const fab = fabricantesMap.get(fabricante.id)!;
            fab.cpks.push(cpk);
            fab.kmTotal += km;
            fab.costoTotal += costoTotal;
        }

        // Convertir a array de estadísticas
        const marcas: BrandCPKStats[] = [];
        for (const [, fab] of fabricantesMap) {
            if (fab.cpks.length === 0) continue;

            const cpkPromedio = fab.cpks.reduce((a, b) => a + b, 0) / fab.cpks.length;
            const cpkMinimo = Math.min(...fab.cpks);
            const cpkMaximo = Math.max(...fab.cpks);

            marcas.push({
                fabricante_id: fab.id,
                fabricante_nombre: fab.nombre,
                cpk_promedio: Number(cpkPromedio.toFixed(4)),
                cpk_minimo: Number(cpkMinimo.toFixed(4)),
                cpk_maximo: Number(cpkMaximo.toFixed(4)),
                total_neumaticos: fab.cpks.length,
                kilometraje_total: fab.kmTotal,
                costo_total: Number(fab.costoTotal.toFixed(2))
            });
        }

        // Ordenar por CPK promedio (menor es mejor)
        marcas.sort((a, b) => a.cpk_promedio - b.cpk_promedio);

        return {
            marcas,
            mejor_marca: marcas.length > 0 ? marcas[0].fabricante_nombre : null,
            peor_marca: marcas.length > 0 ? marcas[marcas.length - 1].fabricante_nombre : null,
            fecha_calculo: new Date().toISOString()
        };
    }

    /**
     * Obtiene el estado general de la flota.
     * Vehículos activos, neumáticos instalados vs stock.
     */
    async getFlotaStatus() {
        // Vehículos
        const totalVehiculos = await prisma.vehiculo.count({ where: { activo: true } });

        // Neumáticos
        const totalNeumaticos = await prisma.neumatico.count({ where: { activo: true, estado_actual: { not: 'DESECHADO' } } });
        const instalados = await prisma.neumatico.count({ where: { activo: true, estado_actual: 'INSTALADO' } });
        const stock = await prisma.neumatico.count({ where: { activo: true, estado_actual: 'EN_STOCK' } });
        const reencauche = await prisma.neumatico.count({ where: { activo: true, estado_actual: 'EN_REENCAUCHE' } });
        const reparacion = await prisma.neumatico.count({ where: { activo: true, estado_actual: 'EN_REPARACION' } });

        // Valor inventario (estimado)
        const valorInventario = await prisma.neumatico.aggregate({
            where: { activo: true, estado_actual: { not: 'DESECHADO' } },
            _sum: { costo_compra: true }
        });

        return {
            vehiculos: { total: totalVehiculos },
            neumaticos: {
                total: totalNeumaticos,
                instalados,
                stock,
                reencauche,
                reparacion,
            },
            valor_inventario: Number(valorInventario._sum.costo_compra || 0)
        };
    }

    /**
     * Obtiene el inventario detallado por almacén.
     */
    async getInventoryStatus() {
        const almacenes = await prisma.almacen.findMany({
            where: { activo: true },
            include: {
                _count: {
                    select: {
                        neumaticos: {
                            where: { activo: true, estado_actual: { not: 'DESECHADO' } }
                        }
                    }
                }
            }
        });

        // Agrupación por fabricante (marca) para stock
        // Prisma groupBy no soporta relaciones, lo hacemos en memoria (o raw query si fuera masivo)
        const stockItems = await prisma.neumatico.findMany({
            where: { estado_actual: 'EN_STOCK', activo: true },
            select: {
                modelo: {
                    select: {
                        fabricante: {
                            select: { nombre: true }
                        }
                    }
                }
            }
        });

        const stockMap = new Map<string, number>();

        for (const item of stockItems) {
            const marca = item.modelo?.fabricante?.nombre || 'Desconocida';
            stockMap.set(marca, (stockMap.get(marca) || 0) + 1);
        }

        const stockDetalle = Array.from(stockMap.entries()).map(([marca, cantidad]) => ({
            marca,
            cantidad
        }));

        // Ordenar por cantidad descendente
        stockDetalle.sort((a, b) => b.cantidad - a.cantidad);

        return {
            almacenes: almacenes.map(a => ({
                id: a.id,
                nombre: a.nombre,
                total_items: a._count.neumaticos
            })),
            stock_por_marca: stockDetalle
        };
    }
}
