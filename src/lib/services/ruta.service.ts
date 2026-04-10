import { prisma } from '@/lib/prisma';
import { Result, ok, err, BusinessError, NotFoundError, ConflictError } from '@/types/result.types';
import { CreateRutaInput, UpdateRutaInput, AssignRutaInput } from '@/lib/validators/ruta.validator';
import { Prisma } from '@prisma/client';

export class RutaService {
    async create(
        empresa_id: string,
        userId: string,
        input: CreateRutaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const tipoRuta = await prisma.tipoRuta.findUnique({
                where: { id: input.tipo_ruta_id, activo: true },
            });

            if (!tipoRuta) {
                return err(new NotFoundError('Tipo de ruta'));
            }

            const ruta = await prisma.ruta.create({
                data: {
                    empresa_id,
                    nombre: input.nombre,
                    origen: input.origen || null,
                    destino: input.destino || null,
                    distancia_km: new Prisma.Decimal(input.distancia_km),
                    tipo_ruta_id: input.tipo_ruta_id,
                    activo: input.activo,
                },
                include: {
                    tipo_ruta: true,
                },
            });

            return ok(ruta);
        } catch (error: any) {
            console.error('[RutaService.create] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Tipo de ruta no encontrado'));
            }
            return err(new BusinessError('Error al crear la ruta', 'CREATE_ERROR', 500));
        }
    }

    async update(
        empresa_id: string,
        userId: string,
        rutaId: string,
        input: UpdateRutaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const ruta = await prisma.ruta.findUnique({
                where: { id: rutaId, empresa_id },
            });

            if (!ruta) {
                return err(new NotFoundError('Ruta'));
            }

            const updateData: any = { ...input };
            if (input.distancia_km !== undefined) {
                updateData.distancia_km = new Prisma.Decimal(input.distancia_km);
            }

            const updated = await prisma.ruta.update({
                where: { id: rutaId, empresa_id },
                data: updateData,
                include: {
                    tipo_ruta: true,
                },
            });

            return ok(updated);
        } catch (error: any) {
            console.error('[RutaService.update] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Ruta'));
            }
            return err(new BusinessError('Error al actualizar la ruta', 'UPDATE_ERROR', 500));
        }
    }

    async delete(
        empresa_id: string,
        rutaId: string
    ): Promise<Result<void, BusinessError>> {
        try {
            const ruta = await prisma.ruta.findUnique({
                where: { id: rutaId, empresa_id },
            });

            if (!ruta) {
                return err(new NotFoundError('Ruta'));
            }

            const vehiculosConRuta = await prisma.vehiculo.count({
                where: { ruta_id: rutaId, activo: true },
            });

            if (vehiculosConRuta > 0) {
                return err(new BusinessError(
                    `No se puede eliminar la ruta porque tiene ${vehiculosConRuta} vehiculo(s) asignado(s)`,
                    'HAS_VEHICULOS',
                    400
                ));
            }

            await prisma.ruta.update({
                where: { id: rutaId, empresa_id },
                data: { activo: false },
            });

            return ok(undefined);
        } catch (error: any) {
            console.error('[RutaService.delete] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Ruta'));
            }
            return err(new BusinessError('Error al eliminar la ruta', 'DELETE_ERROR', 500));
        }
    }

    async getById(
        empresa_id: string,
        rutaId: string
    ): Promise<Result<any, BusinessError>> {
        try {
            const ruta = await prisma.ruta.findUnique({
                where: { id: rutaId, empresa_id, activo: true },
                include: {
                    tipo_ruta: true,
                    vehiculos: {
                        where: { activo: true },
                        select: {
                            id: true,
                            placa: true,
                            numero_economico: true,
                        },
                    },
                },
            });

            if (!ruta) {
                return err(new NotFoundError('Ruta'));
            }

            return ok(ruta);
        } catch (error) {
            console.error('[RutaService.getById] Error:', error);
            return err(new BusinessError('Error al obtener la ruta', 'QUERY_ERROR', 500));
        }
    }

    async getAll(
        empresa_id: string,
        filters?: { activo?: boolean; tipo_ruta_id?: string }
    ): Promise<Result<any[], BusinessError>> {
        try {
            const where: any = { empresa_id };

            if (filters?.activo !== undefined) {
                where.activo = filters.activo;
            }
            if (filters?.tipo_ruta_id) {
                where.tipo_ruta_id = filters.tipo_ruta_id;
            }

            const rutas = await prisma.ruta.findMany({
                where,
                include: {
                    tipo_ruta: true,
                    _count: {
                        select: { vehiculos: { where: { activo: true } } },
                    },
                },
                orderBy: { creado_en: 'desc' },
            });

            return ok(rutas);
        } catch (error) {
            console.error('[RutaService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener rutas', 'QUERY_ERROR', 500));
        }
    }

    async assignToVehiculo(
        empresa_id: string,
        userId: string,
        rutaId: string,
        input: AssignRutaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const ruta = await prisma.ruta.findUnique({
                where: { id: rutaId, empresa_id, activo: true },
            });

            if (!ruta) {
                return err(new NotFoundError('Ruta'));
            }

            const vehiculo = await prisma.vehiculo.findUnique({
                where: { id: input.vehiculo_id, activo: true },
            });

            if (!vehiculo || vehiculo.empresa_id !== empresa_id) {
                return err(new NotFoundError('Vehículo'));
            }

            const updated = await prisma.vehiculo.update({
                where: { id: input.vehiculo_id },
                data: { ruta_id: rutaId },
                include: {
                    ruta_asignada: { include: { tipo_ruta: true } },
                    tipo_vehiculo: true,
                },
            });

            return ok({
                message: `Vehículo ${vehiculo.numero_economico} asignado a ruta ${ruta.nombre}`,
                vehiculo: updated,
            });
        } catch (error: any) {
            console.error('[RutaService.assignToVehiculo] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Ruta o vehículo no encontrado'));
            }
            return err(new BusinessError('Error al asignar vehículo a la ruta', 'ASSIGN_ERROR', 500));
        }
    }
}

export const rutaService = new RutaService();
