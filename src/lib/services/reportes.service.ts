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
    async getCPK(empresaId: string, neumaticoId: string): Promise<CPKMetrics> {
        const neumatico = await prisma.neumatico.findFirst({
            where: {
                id: neumaticoId,
                empresa_id: empresaId
            },
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
    async getDesgastePromedio(empresaId: string, neumaticoId: string): Promise<WearRateMetrics> {
        const neumatico = await prisma.neumatico.findFirst({
            where: {
                id: neumaticoId,
                empresa_id: empresaId
            }
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
    async getComparativoMarcas(empresaId: string): Promise<BrandComparisonResult> {
        // Obtener todos los neumáticos del tenant con km > 0 y sus fabricantes
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
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
    async getFlotaStatus(empresaId: string) {
        // Vehículos
        const totalVehiculos = await prisma.vehiculo.count({ where: { activo: true, empresa_id: empresaId } });

        // Neumáticos
        const totalNeumaticos = await prisma.neumatico.count({ where: { activo: true, empresa_id: empresaId, estado_actual: { not: 'DESECHADO' } } });
        const instalados = await prisma.neumatico.count({ where: { activo: true, empresa_id: empresaId, estado_actual: 'INSTALADO' } });
        const stock = await prisma.neumatico.count({ where: { activo: true, empresa_id: empresaId, estado_actual: 'EN_STOCK' } });
        const reencauche = await prisma.neumatico.count({ where: { activo: true, empresa_id: empresaId, estado_actual: 'EN_REENCAUCHE' } });
        const reparacion = await prisma.neumatico.count({ where: { activo: true, empresa_id: empresaId, estado_actual: 'EN_REPARACION' } });

        // Valor inventario (estimado)
        const valorInventario = await prisma.neumatico.aggregate({
            where: { activo: true, empresa_id: empresaId, estado_actual: { not: 'DESECHADO' } },
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
    async getInventoryStatus(empresaId: string) {
        const almacenes = await prisma.almacen.findMany({
            where: { activo: true, empresa_id: empresaId },
            include: {
                _count: {
                    select: {
                        neumaticos: {
                            where: { activo: true, empresa_id: empresaId, estado_actual: { not: 'DESECHADO' } }
                        }
                    }
                }
            }
        });

        // Agrupación por fabricante (marca) para stock
        // Prisma groupBy no soporta relaciones, lo hacemos en memoria (o raw query si fuera masivo)
        const stockItems = await prisma.neumatico.findMany({
            where: { estado_actual: 'EN_STOCK', activo: true, empresa_id: empresaId },
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

    /**
     * Reporte detallado de rendimiento de toda la flota (DET_REND).
     * Devuelve métricas financieras individuales para tabla masiva.
     */
    async getFleetPerformance(empresaId: string) {
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
                // Opcional: filtrar solo activos o con km > 0
                activo: true
            },
            include: {
                modelo: { include: { fabricante: true } },
                ubicacion_vehiculo: { select: { placa: true, tipo_vehiculo: { select: { nombre: true } } } },
                eventos: { // Optimización: solo traer costos
                    where: { costo_evento: { not: null } },
                    select: { costo_evento: true }
                }
            }
        });

        const details = neumaticos.map(n => {
            const costoCompra = Number(n.costo_compra ?? 0);
            const costoMantenimiento = n.eventos.reduce((sum, e) => sum + Number(e.costo_evento ?? 0), 0);
            const costoTotal = costoCompra + costoMantenimiento;
            const km = toNumber(n.kilometraje_acumulado);

            const cpk = km > 0 ? costoTotal / km : 0;

            // Proyecciones simples (misma lógica que NeumaticoService pero simplificada para bulk)
            const profOriginal = toNumber(n.modelo.profundidad_original_mm);
            const profActual = toNumber(n.profundidad_remanente_actual_mm);
            const profMin = toNumber(n.modelo.profundidad_minima_retiro_mm);

            const desgaste = Math.max(0, profOriginal - profActual);
            const rendimiento = desgaste > 0 ? km / desgaste : 0;
            const remanenteUtil = Math.max(0, profActual - profMin);
            const vidaRestante = rendimiento * remanenteUtil; // si rendimiento 0, esto es 0
            const vidaTotal = km + vidaRestante;
            const cpkProy = vidaTotal > 0 ? costoTotal / vidaTotal : 0;

            return {
                id: n.id,
                serie: n.numero_serie,
                marca: n.modelo.fabricante.nombre,
                modelo: n.modelo.nombre_modelo,
                medida: n.modelo.medida,
                vehiculo: n.ubicacion_vehiculo?.placa || 'ALMACÉN',
                tipo_vehiculo: n.ubicacion_vehiculo?.tipo_vehiculo.nombre || '-',
                estado: n.estado_actual,

                costo_total: Number(costoTotal.toFixed(2)),
                km_actual: Number(km.toFixed(2)),
                cpk_actual: Number(cpk.toFixed(6)),

                prof_actual_mm: Number(profActual.toFixed(2)),
                vida_estimada_km: Number(vidaTotal.toFixed(0)),
                cpk_proyectado: Number(cpkProy.toFixed(6))
            };
        });

        // Ordenar por CPK descendente (los más costosos primero para atención)
        details.sort((a, b) => b.cpk_actual - a.cpk_actual);

        // Resumen global
        const totalCost = details.reduce((sum, d) => sum + d.costo_total, 0);
        const totalKm = details.reduce((sum, d) => sum + d.km_actual, 0);
        const fleetCpk = totalKm > 0 ? totalCost / totalKm : 0;

        return {
            summary: {
                total_neumaticos: details.length,
                costo_flota_total: Number(totalCost.toFixed(2)),
                km_rodados_total: Number(totalKm.toFixed(2)),
                cpk_flota_promedio: Number(fleetCpk.toFixed(6))
            },
            data: details
        };
    }

    /**
     * KPIs de Gestión Avanzada (Reencauchabilidad + Scrap).
     * Fase 6A: Incluye Pareto por CategoriaFalla (FATIGA/MECANICA/OPERACION).
     */
    async getManagementKPIs(empresaId: string) {
        // --- 1. REENCAUCHABILIDAD ---
        const neumaticos = await prisma.neumatico.findMany({
            where: { empresa_id: empresaId, activo: true },
            select: {
                es_reencauchado: true,
                reencauches_realizados: true,
                vehiculo: { select: { tipo_vehiculo: { select: { nombre: true } } } }
            }
        });

        const totalNeus = neumaticos.length;
        const totalReencauchados = neumaticos.filter(n => n.es_reencauchado).length;
        const sumaVidas = neumaticos.reduce((acc, n) => acc + (n.reencauches_realizados || 0), 0);

        const indiceReencauchePerc = totalNeus > 0 ? (totalReencauchados / totalNeus) * 100 : 0;
        const indiceVidasPromedio = totalNeus > 0 ? (sumaVidas / totalNeus) + 1 : 1;

        // Distribución de vidas (0,1,2,3+)
        const distribucionVidas = { '0': 0, '1': 0, '2': 0, '3+': 0 };
        neumaticos.forEach(n => {
            const vidas = n.reencauches_realizados || 0;
            if (vidas === 0) distribucionVidas['0']++;
            else if (vidas === 1) distribucionVidas['1']++;
            else if (vidas === 2) distribucionVidas['2']++;
            else distribucionVidas['3+']++;
        });

        // KPIs por tipo de vehículo
        const kpisPorTipo: Record<string, { total: number; reencauchados: number; vidas: number }> = {};
        neumaticos.forEach(n => {
            const tipo = n.vehiculo?.tipo_vehiculo?.nombre || 'Sin Asignar';
            if (!kpisPorTipo[tipo]) kpisPorTipo[tipo] = { total: 0, reencauchados: 0, vidas: 0 };
            kpisPorTipo[tipo].total++;
            if (n.es_reencauchado) kpisPorTipo[tipo].reencauchados++;
            kpisPorTipo[tipo].vidas += (n.reencauches_realizados || 0);
        });

        const kpisTipoVehiculo = Object.entries(kpisPorTipo).map(([tipo, data]) => ({
            tipo,
            total: data.total,
            reencauchados: data.reencauchados,
            participacion: data.total > 0 ? Number(((data.reencauchados / data.total) * 100).toFixed(1)) : 0,
            indice_vidas: data.total > 0 ? Number((data.vidas / data.total + 1).toFixed(2)) : 1
        }));

        // --- 2. SCRAP (DESECHOS) ---
        const desechos = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
                estado_actual: 'DESECHADO',
                motivo_desecho_id: { not: null }
            },
            include: { motivo_desecho: true }
        });

        // Pareto por Motivo
        const scrapByReason: Record<string, number> = {};
        desechos.forEach(d => {
            const reason = d.motivo_desecho?.nombre || 'Sin Clasificar';
            scrapByReason[reason] = (scrapByReason[reason] || 0) + 1;
        });

        const scrapPareto = Object.entries(scrapByReason)
            .map(([name, count]) => ({ name, value: count }))
            .sort((a, b) => b.value - a.value);

        // Pareto por Categoría de Falla (FATIGA/MECANICA/OPERACION) - Fase 6A
        const scrapByCategory: Record<string, number> = {
            'FATIGA': 0,
            'MECANICA': 0,
            'OPERACION': 0,
            'SIN_CLASIFICAR': 0
        };
        desechos.forEach(d => {
            const categoria = d.motivo_desecho?.categoria_falla || 'SIN_CLASIFICAR';
            scrapByCategory[categoria] = (scrapByCategory[categoria] || 0) + 1;
        });

        const scrapParetoCategoria = Object.entries(scrapByCategory)
            .filter(([, count]) => count > 0)
            .map(([name, count]) => ({ name, value: count }))
            .sort((a, b) => b.value - a.value);

        const totalScrap = desechos.length;
        const tasaScrap = (totalNeus + totalScrap) > 0 ? (totalScrap / (totalNeus + totalScrap)) * 100 : 0;

        return {
            kpis: {
                indice_reencauche_porcentaje: Number(indiceReencauchePerc.toFixed(1)),
                indice_vidas_promedio: Number(indiceVidasPromedio.toFixed(2)),
                total_activos: totalNeus,
                total_desechados: totalScrap,
                tasa_scrap_global: Number(tasaScrap.toFixed(1))
            },
            distribucion_vidas: distribucionVidas,
            kpis_por_tipo_vehiculo: kpisTipoVehiculo,
            charts: {
                scrap_pareto: scrapPareto,
                scrap_pareto_categoria: scrapParetoCategoria
            }
        };
    }

    /**
     * Matriz Semáforo filtrada por Medida con distribución por Eje.
     * Fase 6A.3: Muestra estado de neumáticos agrupados por eje (Direccional/Tracción/Repuesto).
     */
    async getSemaforoByMedida(empresaId: string, medidaFilter?: string) {
        // Obtener neumáticos montados con su posición y modelo
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
                activo: true,
                estado_actual: 'EN_USO',
                ...(medidaFilter ? {
                    modelo: { medida: { contains: medidaFilter } }
                } : {})
            },
            include: {
                modelo: { select: { medida: true, fabricante: { select: { nombre: true } } } },
                posicion_actual: {
                    select: {
                        codigo: true,
                        tipo_eje: true,
                        es_repuesto: true
                    }
                },
                vehiculo: { select: { placa: true, tipo_vehiculo: { select: { nombre: true } } } }
            }
        });

        // Clasificar por tipo de eje
        const porEje: Record<string, { verde: number; amarillo: number; rojo: number; total: number }> = {
            'DIRECCIONAL': { verde: 0, amarillo: 0, rojo: 0, total: 0 },
            'TRACCION': { verde: 0, amarillo: 0, rojo: 0, total: 0 },
            'REPUESTO': { verde: 0, amarillo: 0, rojo: 0, total: 0 }
        };

        // Lista de medidas disponibles para filtro
        const medidasSet = new Set<string>();

        // Detalle por neumático
        const detalle: Array<{
            serie: string;
            medida: string;
            marca: string;
            placa: string;
            posicion: string;
            eje: string;
            remanente_mm: number;
            estado_semaforo: 'VERDE' | 'AMARILLO' | 'ROJO';
        }> = [];

        neumaticos.forEach(n => {
            const medida = n.modelo?.medida || 'Sin Medida';
            medidasSet.add(medida);

            const remanente = toNumber(n.profundidad_remanente);
            const posicionCodigo = n.posicion_actual?.codigo || '';
            const esRepuesto = n.posicion_actual?.es_repuesto || false;

            // Determinar tipo de eje
            let eje = 'TRACCION';
            if (esRepuesto) {
                eje = 'REPUESTO';
            } else if (posicionCodigo.startsWith('1')) {
                eje = 'DIRECCIONAL';
            }

            // Semáforo basado en remanente
            let semaforo: 'VERDE' | 'AMARILLO' | 'ROJO' = 'VERDE';
            if (remanente <= 3) {
                semaforo = 'ROJO';
            } else if (remanente <= 5) {
                semaforo = 'AMARILLO';
            }

            // Acumular estadísticas
            if (porEje[eje]) {
                porEje[eje].total++;
                if (semaforo === 'VERDE') porEje[eje].verde++;
                else if (semaforo === 'AMARILLO') porEje[eje].amarillo++;
                else porEje[eje].rojo++;
            }

            detalle.push({
                serie: n.numero_serie,
                medida,
                marca: n.modelo?.fabricante?.nombre || 'N/A',
                placa: n.vehiculo?.placa || 'Sin Vehículo',
                posicion: posicionCodigo,
                eje,
                remanente_mm: remanente,
                estado_semaforo: semaforo
            });
        });

        // Resumen global
        const totalVerde = Object.values(porEje).reduce((acc, e) => acc + e.verde, 0);
        const totalAmarillo = Object.values(porEje).reduce((acc, e) => acc + e.amarillo, 0);
        const totalRojo = Object.values(porEje).reduce((acc, e) => acc + e.rojo, 0);
        const totalGeneral = totalVerde + totalAmarillo + totalRojo;

        return {
            filtro_aplicado: medidaFilter || null,
            medidas_disponibles: Array.from(medidasSet).sort(),
            resumen: {
                total: totalGeneral,
                verde: totalVerde,
                amarillo: totalAmarillo,
                rojo: totalRojo,
                porcentaje_critico: totalGeneral > 0 ? Number(((totalRojo / totalGeneral) * 100).toFixed(1)) : 0
            },
            distribucion_por_eje: Object.entries(porEje).map(([eje, data]) => ({
                eje,
                ...data,
                porcentaje_rojo: data.total > 0 ? Number(((data.rojo / data.total) * 100).toFixed(1)) : 0
            })),
            detalle: detalle.sort((a, b) => a.remanente_mm - b.remanente_mm) // Más críticos primero
        };
    }
}
