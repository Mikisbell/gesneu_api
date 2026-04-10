import { prisma } from '@/lib/prisma';
import { Result, ok, err, BusinessError, NotFoundError, ConflictError } from '@/types/result.types';
import {
    CreateGarantiaInput,
    ClaimGarantiaInput,
    ResolveGarantiaInput,
    UpdateGarantiaInput,
} from '@/lib/validators/garantia.validator';
import { EstadoGarantia, Prisma } from '@prisma/client';

export class GarantiaService {
    async create(
        empresa_id: string,
        userId: string,
        input: CreateGarantiaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: input.neumatico_id },
                select: { id: true, empresa_id: true },
            });

            if (!neumatico || neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Neumático'));
            }

            if (input.numero_garantia) {
                const existing = await prisma.garantiaNeumatico.findUnique({
                    where: { numero_garantia: input.numero_garantia },
                });
                if (existing) {
                    return err(new ConflictError(`Ya existe una garantía con el número ${input.numero_garantia}`));
                }
            }

            const garantia = await prisma.garantiaNeumatico.create({
                data: {
                    neumatico_id: input.neumatico_id,
                    proveedor_id: input.proveedor_id || null,
                    numero_garantia: input.numero_garantia || null,
                    fecha_inicio: input.fecha_inicio,
                    fecha_fin: input.fecha_fin,
                    kilometraje_max: input.kilometraje_max ? new Prisma.Decimal(input.kilometraje_max) : null,
                    profundidad_min: input.profundidad_min || null,
                    condiciones: input.condiciones || null,
                    estado: EstadoGarantia.VIGENTE,
                    creado_por: userId,
                },
                include: {
                    neumatico: { select: { numero_serie: true, modelo: { select: { nombre_modelo: true } } } },
                    proveedor: { select: { nombre: true } },
                },
            });

            return ok(garantia);
        } catch (error: any) {
            console.error('[GarantiaService.create] Error:', error);
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe una garantía con este número'));
            }
            if (error.code === 'P2025') {
                return err(new NotFoundError('Recurso relacionado no encontrado'));
            }
            return err(new BusinessError('Error al crear la garantía', 'CREATE_ERROR', 500));
        }
    }

    async fileClaim(
        empresa_id: string,
        userId: string,
        garantiaId: string,
        input: ClaimGarantiaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const garantia = await prisma.garantiaNeumatico.findUnique({
                where: { id: garantiaId },
                include: { neumatico: { select: { empresa_id: true } } },
            });

            if (!garantia || garantia.neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Garantía'));
            }

            if (garantia.estado !== EstadoGarantia.VIGENTE) {
                return err(new BusinessError(
                    `Solo se pueden reclamar garantías en estado VIGENTE. Estado actual: ${garantia.estado}`,
                    'INVALID_STATE',
                    400
                ));
            }

            const updated = await prisma.garantiaNeumatico.update({
                where: { id: garantiaId },
                data: {
                    estado: EstadoGarantia.RECLAMADA,
                    fecha_reclamo: input.fecha_reclamo || new Date(),
                    motivo_reclamo: input.motivo_reclamo,
                    actualizado_en: new Date(),
                },
                include: {
                    neumatico: { select: { numero_serie: true } },
                    proveedor: { select: { nombre: true } },
                },
            });

            return ok(updated);
        } catch (error: any) {
            console.error('[GarantiaService.fileClaim] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Garantía'));
            }
            return err(new BusinessError('Error al reclamar la garantía', 'CLAIM_ERROR', 500));
        }
    }

    async resolveClaim(
        empresa_id: string,
        userId: string,
        garantiaId: string,
        input: ResolveGarantiaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const garantia = await prisma.garantiaNeumatico.findUnique({
                where: { id: garantiaId },
                include: { neumatico: { select: { empresa_id: true } } },
            });

            if (!garantia || garantia.neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Garantía'));
            }

            if (garantia.estado !== EstadoGarantia.RECLAMADA) {
                return err(new BusinessError(
                    `Solo se pueden resolver garantías en estado RECLAMADA. Estado actual: ${garantia.estado}`,
                    'INVALID_STATE',
                    400
                ));
            }

            const nuevoEstado = input.monto_reembolso && input.monto_reembolso > 0
                ? EstadoGarantia.APROBADA
                : EstadoGarantia.RECHAZADA;

            const updated = await prisma.garantiaNeumatico.update({
                where: { id: garantiaId },
                data: {
                    estado: nuevoEstado,
                    resolucion: input.resolucion,
                    monto_reembolso: input.monto_reembolso ? new Prisma.Decimal(input.monto_reembolso) : null,
                    actualizado_en: new Date(),
                },
                include: {
                    neumatico: { select: { numero_serie: true } },
                    proveedor: { select: { nombre: true } },
                },
            });

            return ok(updated);
        } catch (error: any) {
            console.error('[GarantiaService.resolveClaim] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Garantía'));
            }
            return err(new BusinessError('Error al resolver el reclamo de garantía', 'RESOLVE_ERROR', 500));
        }
    }

    async getByNeumatico(
        empresa_id: string,
        neumaticoId: string
    ): Promise<Result<any[], BusinessError>> {
        try {
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: neumaticoId },
                select: { id: true, empresa_id: true },
            });

            if (!neumatico || neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Neumático'));
            }

            const garantias = await prisma.garantiaNeumatico.findMany({
                where: { neumatico_id: neumaticoId },
                include: {
                    proveedor: { select: { nombre: true } },
                },
                orderBy: { fecha_inicio: 'desc' },
            });

            return ok(garantias);
        } catch (error) {
            console.error('[GarantiaService.getByNeumatico] Error:', error);
            return err(new BusinessError('Error al obtener garantías del neumático', 'QUERY_ERROR', 500));
        }
    }

    async getAll(
        empresa_id: string,
        filters?: { estado?: string; neumatico_id?: string; proveedor_id?: string }
    ): Promise<Result<any[], BusinessError>> {
        try {
            const where: any = {
                neumatico: {
                    empresa_id,
                    activo: true,
                },
            };

            if (filters?.estado) {
                where.estado = filters.estado;
            }
            if (filters?.neumatico_id) {
                where.neumatico_id = filters.neumatico_id;
            }
            if (filters?.proveedor_id) {
                where.proveedor_id = filters.proveedor_id;
            }

            const garantias = await prisma.garantiaNeumatico.findMany({
                where,
                include: {
                    neumatico: {
                        select: {
                            numero_serie: true,
                            modelo: { select: { nombre_modelo: true, medida: true } },
                        },
                    },
                    proveedor: { select: { nombre: true } },
                },
                orderBy: { creado_en: 'desc' },
            });

            return ok(garantias);
        } catch (error) {
            console.error('[GarantiaService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener garantías', 'QUERY_ERROR', 500));
        }
    }

    async getById(
        empresa_id: string,
        garantiaId: string
    ): Promise<Result<any, BusinessError>> {
        try {
            const garantia = await prisma.garantiaNeumatico.findUnique({
                where: { id: garantiaId },
                include: {
                    neumatico: {
                        select: {
                            id: true,
                            empresa_id: true,
                            numero_serie: true,
                            modelo: { select: { nombre_modelo: true, medida: true } },
                        },
                    },
                    proveedor: { select: { nombre: true } },
                },
            });

            if (!garantia || garantia.neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Garantía'));
            }

            return ok(garantia);
        } catch (error) {
            console.error('[GarantiaService.getById] Error:', error);
            return err(new BusinessError('Error al obtener la garantía', 'QUERY_ERROR', 500));
        }
    }

    async update(
        empresa_id: string,
        userId: string,
        garantiaId: string,
        input: UpdateGarantiaInput
    ): Promise<Result<any, BusinessError>> {
        try {
            const garantia = await prisma.garantiaNeumatico.findUnique({
                where: { id: garantiaId },
                include: { neumatico: { select: { empresa_id: true } } },
            });

            if (!garantia || garantia.neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Garantía'));
            }

            const updateData: any = { ...input };
            if (input.fecha_inicio) updateData.fecha_inicio = input.fecha_inicio;
            if (input.fecha_fin) updateData.fecha_fin = input.fecha_fin;
            if (input.kilometraje_max !== undefined) updateData.kilometraje_max = new Prisma.Decimal(input.kilometraje_max);
            if (input.profundidad_min !== undefined) updateData.profundidad_min = input.profundidad_min;
            updateData.actualizado_en = new Date();

            const updated = await prisma.garantiaNeumatico.update({
                where: { id: garantiaId },
                data: updateData,
                include: {
                    neumatico: { select: { numero_serie: true } },
                    proveedor: { select: { nombre: true } },
                },
            });

            return ok(updated);
        } catch (error: any) {
            console.error('[GarantiaService.update] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Garantía'));
            }
            return err(new BusinessError('Error al actualizar la garantía', 'UPDATE_ERROR', 500));
        }
    }

    async delete(
        empresa_id: string,
        garantiaId: string
    ): Promise<Result<void, BusinessError>> {
        try {
            const garantia = await prisma.garantiaNeumatico.findUnique({
                where: { id: garantiaId },
                include: { neumatico: { select: { empresa_id: true } } },
            });

            if (!garantia || garantia.neumatico.empresa_id !== empresa_id) {
                return err(new NotFoundError('Garantía'));
            }

            if (garantia.estado !== EstadoGarantia.VIGENTE) {
                return err(new BusinessError(
                    'Solo se pueden eliminar garantías en estado VIGENTE',
                    'INVALID_STATE',
                    400
                ));
            }

            await prisma.garantiaNeumatico.delete({
                where: { id: garantiaId },
            });

            return ok(undefined);
        } catch (error: any) {
            console.error('[GarantiaService.delete] Error:', error);
            if (error.code === 'P2025') {
                return err(new NotFoundError('Garantía'));
            }
            return err(new BusinessError('Error al eliminar la garantía', 'DELETE_ERROR', 500));
        }
    }
}

export const garantiaService = new GarantiaService();
