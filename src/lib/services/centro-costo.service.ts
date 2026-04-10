import { prisma } from '@/lib/prisma';
import { Result, ok, err, BusinessError, NotFoundError, ConflictError } from '@/types/result.types';
import { CreateCentroCostoInput, UpdateCentroCostoInput } from '@/lib/validators/centro-costo.validator';

export class CentroCostoService {
    async create(
        empresa_id: string,
        userId: string,
        input: CreateCentroCostoInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const existing = await prisma.centroCosto.findUnique({
                where: { empresa_id_codigo: { empresa_id, codigo: input.codigo } },
            });

            if (existing) {
                return err(new ConflictError(`Ya existe un centro de costo con el código ${input.codigo}`));
            }

            const centroCosto = await prisma.centroCosto.create({
                data: {
                    empresa_id,
                    codigo: input.codigo,
                    nombre: input.nombre,
                    area_negocio: input.area_negocio || null,
                    activo: input.activo,
                },
            });

            return ok(centroCosto);
        } catch (error: any) {
            console.error('[CentroCostoService.create] Error:', error);
            console.error('[CentroCostoService.create] Code:', error?.code, 'Meta:', JSON.stringify(error?.meta), 'Message:', error?.message);
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe un centro de costo con este código'));
            }
            return err(new BusinessError(`Error al crear el centro de costo: ${error?.message || 'unknown'}`, 'CREATE_ERROR', 500));
        }
    }

    async update(
        empresa_id: string,
        userId: string,
        centroCostoId: string,
        input: UpdateCentroCostoInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const centroCosto = await prisma.centroCosto.findUnique({
                where: { id: centroCostoId, empresa_id },
            });

            if (!centroCosto) {
                return err(new NotFoundError('Centro de costo'));
            }

            if (input.codigo && input.codigo !== centroCosto.codigo) {
                const existing = await prisma.centroCosto.findUnique({
                    where: { empresa_id_codigo: { empresa_id, codigo: input.codigo } },
                });
                if (existing) {
                    return err(new ConflictError(`Ya existe un centro de costo con el código ${input.codigo}`));
                }
            }

            const updated = await prisma.centroCosto.update({
                where: { id: centroCostoId, empresa_id },
                data: input,
            });

            return ok(updated);
        } catch (error: any) {
            console.error('[CentroCostoService.update] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe un centro de costo con este código'));
            }
            if (error.code === 'P2025') {
                return err(new NotFoundError('Centro de costo'));
            }
            return err(new BusinessError('Error al actualizar el centro de costo', 'UPDATE_ERROR', 500));
        }
    }

    async delete(
        empresa_id: string,
        centroCostoId: string
    ): Promise<Result<void, BusinessError>> {
        try {
            const centroCosto = await prisma.centroCosto.findUnique({
                where: { id: centroCostoId, empresa_id },
            });

            if (!centroCosto) {
                return err(new NotFoundError('Centro de costo'));
            }

            const vehiculosConCentro = await prisma.vehiculo.count({
                where: { centro_costo_id: centroCostoId, activo: true },
            });

            if (vehiculosConCentro > 0) {
                return err(new BusinessError(
                    `No se puede eliminar el centro de costo porque tiene ${vehiculosConCentro} vehiculo(s) asociado(s)`,
                    'HAS_VEHICULOS',
                    400
                ));
            }

            await prisma.centroCosto.update({
                where: { id: centroCostoId, empresa_id },
                data: { activo: false },
            });

            return ok(undefined);
        } catch (error: any) {
            console.error('[CentroCostoService.delete] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Centro de costo'));
            }
            return err(new BusinessError('Error al eliminar el centro de costo', 'DELETE_ERROR', 500));
        }
    }

    async getById(
        empresa_id: string,
        centroCostoId: string
    ): Promise<Result<any, BusinessError>> {
        try {
            const centroCosto = await prisma.centroCosto.findUnique({
                where: { id: centroCostoId, empresa_id, activo: true },
                include: {
                    _count: {
                        select: { vehiculos: { where: { activo: true } } },
                    },
                },
            });

            if (!centroCosto) {
                return err(new NotFoundError('Centro de costo'));
            }

            return ok(centroCosto);
        } catch (error) {
            console.error('[CentroCostoService.getById] Error:', error);
            return err(new BusinessError('Error al obtener el centro de costo', 'QUERY_ERROR', 500));
        }
    }

    async getAll(
        empresa_id: string,
        filters?: { activo?: boolean; search?: string }
    ): Promise<Result<any[], BusinessError>> {
        try {
            const where: any = { empresa_id };

            if (filters?.activo !== undefined) {
                where.activo = filters.activo;
            }
            if (filters?.search) {
                where.OR = [
                    { nombre: { contains: filters.search, mode: 'insensitive' } },
                    { codigo: { contains: filters.search, mode: 'insensitive' } },
                    { area_negocio: { contains: filters.search, mode: 'insensitive' } },
                ];
            }

            const centrosCosto = await prisma.centroCosto.findMany({
                where,
                include: {
                    _count: {
                        select: { vehiculos: { where: { activo: true } } },
                    },
                },
                orderBy: { creado_en: 'desc' },
            });

            return ok(centrosCosto);
        } catch (error) {
            console.error('[CentroCostoService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener centros de costo', 'QUERY_ERROR', 500));
        }
    }
}

export const centroCostoService = new CentroCostoService();
