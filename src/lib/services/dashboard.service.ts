import { prisma } from '@/lib/prisma';
import { EstadoNeumaticoEnum } from '@prisma/client';

// ============ REPORTE INVENTARIO ============
export interface InventarioFilters {
    almacen_id?: string;
    estado?: EstadoNeumaticoEnum;
    modelo_id?: string;
}

export interface InventarioAgrupado {
    almacen: { id: string; nombre: string } | null;
    estado: EstadoNeumaticoEnum;
    modelo: { id: string; nombre: string; medida: string };
    cantidad: number;
}

export interface ReporteInventario {
    total_neumaticos: number;
    por_estado: { estado: string; cantidad: number }[];
    por_almacen: { almacen: string; cantidad: number }[];
    detalle: InventarioAgrupado[];
}

// ============ REPORTE RENDIMIENTO ============
export interface RendimientoNeumatico {
    neumatico_id: string;
    numero_serie: string;
    modelo: string;
    cpk: number;
    kilometraje: number;
    estado: string;
}

export interface ReporteRendimiento {
    top_mejores: RendimientoNeumatico[];
    top_peores: RendimientoNeumatico[];
    promedio_cpk: number;
}

// ============ REPORTE DESECHOS ============
export interface ReporteDesechos {
    total_desechados: number;
    por_motivo: { motivo: string; cantidad: number; porcentaje: number }[];
    por_mes: { mes: string; cantidad: number }[];
}

export class DashboardService {
    /**
     * Reporte de inventario agrupado por almacén, estado y modelo
     */
    async getReporteInventario(filters: InventarioFilters = {}): Promise<ReporteInventario> {
        const where: any = { activo: true };
        if (filters.almacen_id) where.ubicacion_almacen_id = filters.almacen_id;
        if (filters.estado) where.estado_actual = filters.estado;
        if (filters.modelo_id) where.modelo_id = filters.modelo_id;

        // Total
        const total = await prisma.neumatico.count({ where });

        // Por estado
        const porEstado = await prisma.neumatico.groupBy({
            by: ['estado_actual'],
            where: { activo: true },
            _count: true
        });

        // Por almacén (solo los que están EN_STOCK)
        const porAlmacen = await prisma.neumatico.groupBy({
            by: ['ubicacion_almacen_id'],
            where: { activo: true, estado_actual: 'EN_STOCK' },
            _count: true
        });

        // Obtener nombres de almacenes
        const almacenes = await prisma.almacen.findMany({
            select: { id: true, nombre: true }
        });
        const almacenMap = new Map(almacenes.map(a => [a.id, a.nombre]));

        // Detalle con modelo
        const neumaticos = await prisma.neumatico.findMany({
            where,
            include: {
                modelo: { select: { id: true, nombre: true, medida: true } },
                ubicacion_almacen: { select: { id: true, nombre: true } }
            },
            take: 100
        });

        // Agrupar para detalle
        const detalleMap = new Map<string, InventarioAgrupado>();
        neumaticos.forEach(n => {
            const key = `${n.ubicacion_almacen_id || 'null'}-${n.estado_actual}-${n.modelo_id}`;
            if (!detalleMap.has(key)) {
                detalleMap.set(key, {
                    almacen: n.ubicacion_almacen,
                    estado: n.estado_actual,
                    modelo: n.modelo,
                    cantidad: 0
                });
            }
            detalleMap.get(key)!.cantidad++;
        });

        return {
            total_neumaticos: total,
            por_estado: porEstado.map(p => ({
                estado: p.estado_actual,
                cantidad: p._count
            })),
            por_almacen: porAlmacen.map(p => ({
                almacen: almacenMap.get(p.ubicacion_almacen_id!) || 'Sin almacén',
                cantidad: p._count
            })),
            detalle: Array.from(detalleMap.values())
        };
    }

    /**
     * Reporte de rendimiento: mejores y peores neumáticos por CPK
     */
    async getReporteRendimiento(limit: number = 10): Promise<ReporteRendimiento> {
        // Obtener neumáticos con km > 0 para calcular CPK
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                kilometraje_acumulado: { gt: 0 },
                activo: true
            },
            include: {
                modelo: { select: { nombre: true } },
                eventos: {
                    where: { costo_evento: { not: null } },
                    select: { costo_evento: true }
                }
            }
        });

        // Calcular CPK para cada uno
        const conCpk: RendimientoNeumatico[] = neumaticos.map(n => {
            const costoCompra = Number(n.costo_compra?.toString() ?? 0);
            const costoEventos = n.eventos.reduce((acc, e) =>
                acc + Number(e.costo_evento?.toString() ?? 0), 0);
            const km = n.kilometraje_acumulado || 1;
            const cpk = (costoCompra + costoEventos) / km;

            return {
                neumatico_id: n.id,
                numero_serie: n.numero_serie,
                modelo: n.modelo.nombre,
                cpk: Number(cpk.toFixed(4)),
                kilometraje: km,
                estado: n.estado_actual
            };
        });

        // Ordenar
        conCpk.sort((a, b) => a.cpk - b.cpk);

        const promedio = conCpk.length > 0
            ? conCpk.reduce((acc, n) => acc + n.cpk, 0) / conCpk.length
            : 0;

        return {
            top_mejores: conCpk.slice(0, limit),
            top_peores: conCpk.slice(-limit).reverse(),
            promedio_cpk: Number(promedio.toFixed(4))
        };
    }

    /**
     * Reporte de desechos: análisis por motivo
     */
    async getReporteDesechos(): Promise<ReporteDesechos> {
        // Contar desechados
        const total = await prisma.neumatico.count({
            where: { estado_actual: 'DESECHADO' }
        });

        // Eventos de desecho con motivo
        const eventosDesecho = await prisma.eventoNeumatico.findMany({
            where: { tipo_evento: 'DESECHO' },
            include: {
                motivo_desecho: { select: { descripcion: true } }
            }
        });

        // Agrupar por motivo
        const motivoCount = new Map<string, number>();
        eventosDesecho.forEach(e => {
            const motivo = e.motivo_desecho?.descripcion || 'Sin motivo';
            motivoCount.set(motivo, (motivoCount.get(motivo) || 0) + 1);
        });

        // Agrupar por mes
        const mesCount = new Map<string, number>();
        eventosDesecho.forEach(e => {
            const mes = e.fecha_evento.toISOString().slice(0, 7); // YYYY-MM
            mesCount.set(mes, (mesCount.get(mes) || 0) + 1);
        });

        const totalEventos = eventosDesecho.length || 1;

        return {
            total_desechados: total,
            por_motivo: Array.from(motivoCount.entries()).map(([motivo, cantidad]) => ({
                motivo,
                cantidad,
                porcentaje: Number(((cantidad / totalEventos) * 100).toFixed(1))
            })).sort((a, b) => b.cantidad - a.cantidad),
            por_mes: Array.from(mesCount.entries()).map(([mes, cantidad]) => ({
                mes,
                cantidad
            })).sort((a, b) => a.mes.localeCompare(b.mes))
        };
    }
}
