import { prisma } from '@/lib/prisma';
import {
    CreateBitacoraMantenimientoInput,
    UpdateBitacoraMantenimientoInput
} from '@/lib/validators/bitacora-mantenimiento.validator';
import {
    Result,
    ok,
    err,
    BusinessError,
    NotFoundError
} from '@/types/result.types';
import { Prisma } from '@prisma/client';

export interface BitacoraMantenimientoFilters {
    tipo_operacion?: string;
    vehiculo_id?: string;
    fecha_desde?: Date;
    fecha_hasta?: Date;
    proveedor_id?: string;
}

export class BitacoraMantenimientoService {
    async create(
        data: CreateBitacoraMantenimientoInput,
        creado_por: string
    ): Promise<Result<any>> {
        try {
            const bitacora = await prisma.bitacoraMantenimiento.create({
                data: {
                    vehiculo_id: data.vehiculo_id,
                    tipo_operacion: data.tipo_operacion as any,
                    fecha_programada: data.fecha_programada || null,
                    fecha_realizada: data.fecha_realizada || new Date(),
                    kilometraje: data.kilometraje ? new Prisma.Decimal(data.kilometraje) : null,
                    horometro: data.horometro ? new Prisma.Decimal(data.horometro) : null,
                    costo: data.costo !== undefined && data.costo !== null ? new Prisma.Decimal(data.costo) : null,
                    proveedor_id: data.proveedor_id || null,
                    responsable: data.responsable || null,
                    observaciones: data.observaciones || null,
                    evidencia_url: data.evidencia_url || null,
                    creado_por
                },
                include: {
                    proveedor: true
                }
            });

            return ok(bitacora);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.create] Error:', error);
            return err(new BusinessError('Error al crear registro de bitacora', 'CREATE_ERROR', 500));
        }
    }

    async getAll(
        empresa_id: string,
        filters?: BitacoraMantenimientoFilters
    ): Promise<Result<any[]>> {
        try {
            const where: any = {
                vehiculo: {
                    empresa_id
                }
            };

            if (filters?.tipo_operacion) {
                where.tipo_operacion = filters.tipo_operacion;
            }
            if (filters?.vehiculo_id) {
                where.vehiculo_id = filters.vehiculo_id;
            }
            if (filters?.fecha_desde || filters?.fecha_hasta) {
                where.fecha_realizada = {};
                if (filters.fecha_desde) {
                    where.fecha_realizada.gte = filters.fecha_desde;
                }
                if (filters.fecha_hasta) {
                    where.fecha_realizada.lte = filters.fecha_hasta;
                }
            }
            if (filters?.proveedor_id) {
                where.proveedor_id = filters.proveedor_id;
            }

            const bitacoras = await prisma.bitacoraMantenimiento.findMany({
                where,
                include: {
                    proveedor: true
                },
                orderBy: {
                    fecha_realizada: 'desc'
                }
            });

            return ok(bitacoras);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener registros de bitacora', 'QUERY_ERROR', 500));
        }
    }

    async getById(id: string, empresa_id: string): Promise<Result<any>> {
        try {
            const bitacora = await prisma.bitacoraMantenimiento.findUnique({
                where: { id },
                include: {
                    vehiculo: {
                        select: { empresa_id: true }
                    },
                    proveedor: true
                }
            });

            if (!bitacora) {
                return err(new NotFoundError('Registro de bitacora'));
            }

            if (bitacora.vehiculo.empresa_id !== empresa_id) {
                return err(new BusinessError('No tienes acceso a este registro de bitacora', 'FORBIDDEN', 403));
            }

            return ok(bitacora);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.getById] Error:', error);
            return err(new BusinessError('Error al obtener registro de bitacora', 'QUERY_ERROR', 500));
        }
    }

    async update(
        id: string,
        data: UpdateBitacoraMantenimientoInput,
        empresa_id: string
    ): Promise<Result<any>> {
        try {
            const existing = await prisma.bitacoraMantenimiento.findUnique({
                where: { id },
                include: {
                    vehiculo: {
                        select: { empresa_id: true }
                    }
                }
            });

            if (!existing) {
                return err(new NotFoundError('Registro de bitacora'));
            }

            if (existing.vehiculo.empresa_id !== empresa_id) {
                return err(new BusinessError('No tienes acceso a este registro de bitacora', 'FORBIDDEN', 403));
            }

            const updateData: any = {};

            if (data.tipo_operacion !== undefined) {
                updateData.tipo_operacion = data.tipo_operacion;
            }
            if (data.fecha_programada !== undefined) {
                updateData.fecha_programada = data.fecha_programada;
            }
            if (data.fecha_realizada !== undefined) {
                updateData.fecha_realizada = data.fecha_realizada;
            }
            if (data.kilometraje !== undefined) {
                updateData.kilometraje = new Prisma.Decimal(data.kilometraje);
            }
            if (data.horometro !== undefined) {
                updateData.horometro = new Prisma.Decimal(data.horometro);
            }
            if (data.costo !== undefined) {
                updateData.costo = new Prisma.Decimal(data.costo);
            }
            if (data.proveedor_id !== undefined) {
                updateData.proveedor_id = data.proveedor_id;
            }
            if (data.responsable !== undefined) {
                updateData.responsable = data.responsable;
            }
            if (data.observaciones !== undefined) {
                updateData.observaciones = data.observaciones;
            }
            if (data.evidencia_url !== undefined) {
                updateData.evidencia_url = data.evidencia_url;
            }

            const updated = await prisma.bitacoraMantenimiento.update({
                where: { id },
                data: updateData,
                include: {
                    proveedor: true
                }
            });

            return ok(updated);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.update] Error:', error);
            return err(new BusinessError('Error al actualizar registro de bitacora', 'UPDATE_ERROR', 500));
        }
    }

    async delete(id: string, empresa_id: string): Promise<Result<void>> {
        try {
            const existing = await prisma.bitacoraMantenimiento.findUnique({
                where: { id },
                include: {
                    vehiculo: {
                        select: { empresa_id: true }
                    }
                }
            });

            if (!existing) {
                return err(new NotFoundError('Registro de bitacora'));
            }

            if (existing.vehiculo.empresa_id !== empresa_id) {
                return err(new BusinessError('No tienes acceso a este registro de bitacora', 'FORBIDDEN', 403));
            }

            await prisma.bitacoraMantenimiento.delete({
                where: { id }
            });

            return ok(undefined);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.delete] Error:', error);
            return err(new BusinessError('Error al eliminar registro de bitacora', 'DELETE_ERROR', 500));
        }
    }

    async getByVehiculo(
        vehiculoId: string,
        empresa_id: string
    ): Promise<Result<any[]>> {
        try {
            const vehiculo = await prisma.vehiculo.findUnique({
                where: { id: vehiculoId }
            });

            if (!vehiculo || vehiculo.empresa_id !== empresa_id) {
                return err(new NotFoundError('Vehiculo'));
            }

            const bitacoras = await prisma.bitacoraMantenimiento.findMany({
                where: { vehiculo_id: vehiculoId },
                include: {
                    proveedor: true
                },
                orderBy: {
                    fecha_realizada: 'desc'
                }
            });

            return ok(bitacoras);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.getByVehiculo] Error:', error);
            return err(new BusinessError('Error al obtener registros del vehiculo', 'QUERY_ERROR', 500));
        }
    }

    async getByTipo(
        empresa_id: string,
        tipoOperacion: string
    ): Promise<Result<any[]>> {
        try {
            const bitacoras = await prisma.bitacoraMantenimiento.findMany({
                where: {
                    tipo_operacion: tipoOperacion as any,
                    vehiculo: {
                        empresa_id
                    }
                },
                include: {
                    proveedor: true
                },
                orderBy: {
                    fecha_realizada: 'desc'
                }
            });

            return ok(bitacoras);
        } catch (error) {
            console.error('[BitacoraMantenimientoService.getByTipo] Error:', error);
            return err(new BusinessError('Error al obtener registros por tipo', 'QUERY_ERROR', 500));
        }
    }

    async getCostosByPeriodo(
        empresa_id: string,
        fecha_desde: Date,
        fecha_hasta: Date
    ): Promise<Result<any>> {
        try {
            const bitacoras = await prisma.bitacoraMantenimiento.findMany({
                where: {
                    vehiculo: {
                        empresa_id
                    },
                    fecha_realizada: {
                        gte: fecha_desde,
                        lte: fecha_hasta
                    },
                    costo: {
                        not: null
                    }
                },
                select: {
                    costo: true,
                    tipo_operacion: true,
                    fecha_realizada: true
                }
            });

            const totalCosto = bitacoras.reduce((sum, b) => {
                return sum + (b.costo ? parseFloat(b.costo.toString()) : 0);
            }, 0);

            const costosPorTipo = bitacoras.reduce((acc, b) => {
                const tipo = b.tipo_operacion;
                const costo = b.costo ? parseFloat(b.costo.toString()) : 0;
                if (!acc[tipo]) {
                    acc[tipo] = 0;
                }
                acc[tipo] += costo;
                return acc;
            }, {} as Record<string, number>);

            return ok({
                totalCosto,
                totalRegistros: bitacoras.length,
                costosPorTipo,
                periodo: {
                    desde: fecha_desde.toISOString(),
                    hasta: fecha_hasta.toISOString()
                }
            });
        } catch (error) {
            console.error('[BitacoraMantenimientoService.getCostosByPeriodo] Error:', error);
            return err(new BusinessError('Error al calcular costos por periodo', 'QUERY_ERROR', 500));
        }
    }
}

export const bitacoraMantenimientoService = new BitacoraMantenimientoService();
