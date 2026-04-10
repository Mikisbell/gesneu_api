import { prisma } from '@/lib/prisma';
import { Result, ok, err, BusinessError, NotFoundError, ConflictError } from '@/types/result.types';
import { CreateInventarioParamInput, TransferenciaStockInput, ReorderPointInput } from '@/lib/validators/inventario.validator';

export interface StockByAlmacenResult {
    almacen_id: string;
    almacen_codigo: string;
    almacen_nombre: string;
    total_neumaticos: number;
    por_estado: Record<string, number>;
    por_modelo: Array<{
        modelo_id: string;
        modelo_nombre: string;
        medida: string;
        cantidad: number;
    }>;
}

export interface StockSummaryResult {
    total_neumaticos: number;
    por_estado: Record<string, number>;
    por_almacen: Array<{
        almacen_id: string;
        almacen_codigo: string;
        almacen_nombre: string;
        cantidad: number;
    }>;
    con_stock_bajo: Array<{
        almacen_id: string;
        modelo_id: string | null;
        stock_minimo: number;
        cantidad_actual: number;
    }>;
}

export class InventarioService {
    async getStockByAlmacen(empresa_id: string, almacen_id?: string): Promise<Result<StockByAlmacenResult[], BusinessError>> {
        try {
            const where: any = {
                empresa_id,
                activo: true,
                ubicacion_almacen_id: { not: null },
            };

            if (almacen_id) {
                where.ubicacion_almacen_id = almacen_id;
            }

            const neumaticos = await prisma.neumatico.findMany({
                where,
                include: {
                    ubicacion_almacen: true,
                    modelo: { include: { fabricante: true } },
                },
            });

            const almacenMap = new Map<string, StockByAlmacenResult>();

            for (const neum of neumaticos) {
                const almacen = neum.ubicacion_almacen;
                if (!almacen) continue;

                if (!almacenMap.has(almacen.id)) {
                    almacenMap.set(almacen.id, {
                        almacen_id: almacen.id,
                        almacen_codigo: almacen.codigo,
                        almacen_nombre: almacen.nombre,
                        total_neumaticos: 0,
                        por_estado: {},
                        por_modelo: [],
                    });
                }

                const entry = almacenMap.get(almacen.id)!;
                entry.total_neumaticos++;

                entry.por_estado[neum.estado_actual] = (entry.por_estado[neum.estado_actual] || 0) + 1;

                const modeloKey = neum.modelo_id;
                let modeloEntry = entry.por_modelo.find(m => m.modelo_id === modeloKey);
                if (!modeloEntry) {
                    modeloEntry = {
                        modelo_id: neum.modelo_id,
                        modelo_nombre: neum.modelo.nombre_modelo,
                        medida: neum.modelo.medida,
                        cantidad: 0,
                    };
                    entry.por_modelo.push(modeloEntry);
                }
                modeloEntry.cantidad++;
            }

            return ok(Array.from(almacenMap.values()));
        } catch (error) {
            console.error('[InventarioService.getStockByAlmacen] Error:', error);
            return err(new BusinessError('Error al obtener stock por almacén', 'QUERY_ERROR', 500));
        }
    }

    async transferirStock(
        empresa_id: string,
        userId: string,
        input: TransferenciaStockInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const { neumatico_id, almacen_origen_id, almacen_destino_id, observaciones, fecha_evento } = input;

            const neumatico = await prisma.neumatico.findUnique({
                where: { id: neumatico_id },
                include: { ubicacion_almacen: true },
            });

            if (!neumatico || neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Neumático'));
            }

            if (neumatico.ubicacion_almacen_id !== almacen_origen_id) {
                return err(new BusinessError(
                    `El neumático no se encuentra en el almacén origen especificado. Está en ${neumatico.ubicacion_almacen?.codigo || 'desconocido'}`,
                    'INVALID_ORIGIN',
                    400
                ));
            }

            const almacenDestino = await prisma.almacen.findUnique({
                where: { id: almacen_destino_id, activo: true },
            });

            if (!almacenDestino) {
                return err(new NotFoundError('Almacén destino'));
            }

            const now = fecha_evento || new Date();

            await prisma.$transaction(async (tx) => {
                await tx.neumatico.update({
                    where: { id: neumatico_id },
                    data: {
                        ubicacion_almacen_id: almacen_destino_id,
                        estado_actual: 'EN_TRANSITO',
                        actualizado_en: now,
                        actualizado_por: userId,
                    },
                });

                await tx.eventoNeumatico.create({
                    data: {
                        tipo_evento: 'MOVIMIENTO_ENTRE_ALMACENES',
                        neumatico_id,
                        fecha_evento: now,
                        almacen_destino_id: almacen_destino_id,
                        notas: observaciones || `Transferencia desde ${almacen_origen_id} a ${almacen_destino_id}`,
                        creado_por: userId,
                    },
                });
            });

            const updated = await prisma.neumatico.findUnique({
                where: { id: neumatico_id },
                include: {
                    ubicacion_almacen: true,
                    modelo: true,
                },
            });

            return ok({
                message: 'Transferencia realizada exitosamente',
                neumatico: updated,
            });
        } catch (error: any) {
            console.error('[InventarioService.transferirStock] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Recurso no encontrado'));
            }
            return err(new BusinessError('Error al transferir stock', 'TRANSFER_ERROR', 500));
        }
    }

    async setReorderPoint(
        empresa_id: string,
        userId: string,
        input: ReorderPointInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const { almacen_id, modelo_id, stock_minimo, stock_maximo, punto_reorden, cantidad_reorden, lead_time_dias } = input;

            const where: any = {};
            if (almacen_id) {
                const almacen = await prisma.almacen.findUnique({
                    where: { id: almacen_id, activo: true },
                });
                if (!almacen) {
                    return err(new NotFoundError('Almacén'));
                }
                where.almacen_id = almacen_id;
            }

            if (modelo_id) {
                const modelo = await prisma.modeloNeumatico.findUnique({
                    where: { id: modelo_id, activo: true },
                });
                if (!modelo) {
                    return err(new NotFoundError('Modelo de neumático'));
                }
                where.modelo_id = modelo_id;
            }

            if (Object.keys(where).length === 0) {
                return err(new BusinessError('Debe especificar al menos almacen_id o modelo_id', 'MISSING_PARAMS', 400));
            }

            const existing = await prisma.parametroInventario.findFirst({ where });

            const updateData: any = {};
            if (stock_minimo !== undefined) updateData.stock_minimo = stock_minimo;
            if (stock_maximo !== undefined) updateData.stock_maximo = stock_maximo;
            if (punto_reorden !== undefined) updateData.punto_reorden = punto_reorden;
            if (cantidad_reorden !== undefined) updateData.cantidad_reorden = cantidad_reorden;
            if (lead_time_dias !== undefined) updateData.lead_time_dias = lead_time_dias;

            let result;
            if (existing) {
                result = await prisma.parametroInventario.update({
                    where: { id: existing.id },
                    data: updateData,
                });
            } else {
                result = await prisma.parametroInventario.create({
                    data: {
                        ...where,
                        ...updateData,
                    },
                });
            }

            return ok({
                message: existing ? 'Punto de reorden actualizado' : 'Punto de reorden creado',
                parametro: result,
            });
        } catch (error: any) {
            console.error('[InventarioService.setReorderPoint] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Recurso no encontrado'));
            }
            return err(new BusinessError('Error al configurar punto de reorden', 'REORDER_ERROR', 500));
        }
    }

    async getStockSummary(empresa_id: string): Promise<Result<StockSummaryResult, BusinessError>> {
        try {
            const neumaticos = await prisma.neumatico.findMany({
                where: {
                    empresa_id,
                    activo: true,
                    ubicacion_almacen_id: { not: null },
                },
                include: {
                    ubicacion_almacen: true,
                },
            });

            const porEstado: Record<string, number> = {};
            const porAlmacenMap = new Map<string, { almacen_id: string; almacen_codigo: string; almacen_nombre: string; cantidad: number }>();

            for (const neum of neumaticos) {
                porEstado[neum.estado_actual] = (porEstado[neum.estado_actual] || 0) + 1;

                const almacen = neum.ubicacion_almacen;
                if (!almacen) continue;

                if (!porAlmacenMap.has(almacen.id)) {
                    porAlmacenMap.set(almacen.id, {
                        almacen_id: almacen.id,
                        almacen_codigo: almacen.codigo,
                        almacen_nombre: almacen.nombre,
                        cantidad: 0,
                    });
                }
                porAlmacenMap.get(almacen.id)!.cantidad++;
            }

            const paramsReorder = await prisma.parametroInventario.findMany({
                where: { activo: true },
                include: { almacen: true },
            });

            const conStockBajo: Array<{
                almacen_id: string;
                modelo_id: string | null;
                stock_minimo: number;
                cantidad_actual: number;
            }> = [];

            for (const param of paramsReorder) {
                const where: any = { empresa_id, activo: true, ubicacion_almacen_id: { not: null } };
                if (param.almacen_id) where.ubicacion_almacen_id = param.almacen_id;

                const count = await prisma.neumatico.count({ where });
                if (count <= param.stock_minimo) {
                    conStockBajo.push({
                        almacen_id: param.almacen_id || 'N/A',
                        modelo_id: param.modelo_id,
                        stock_minimo: param.stock_minimo,
                        cantidad_actual: count,
                    });
                }
            }

            return ok({
                total_neumaticos: neumaticos.length,
                por_estado: porEstado,
                por_almacen: Array.from(porAlmacenMap.values()),
                con_stock_bajo: conStockBajo,
            });
        } catch (error) {
            console.error('[InventarioService.getStockSummary] Error:', error);
            return err(new BusinessError('Error al obtener resumen de stock', 'SUMMARY_ERROR', 500));
        }
    }
}

export const inventarioService = new InventarioService();
