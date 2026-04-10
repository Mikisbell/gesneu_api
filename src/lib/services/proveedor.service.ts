import { prisma } from '@/lib/prisma';
import { CreateProveedorDTO, UpdateProveedorDTO, ProveedorResponse } from '@/types/domain/proveedor.types';
import { ProveedorId } from '@/types/branded.types';
import { Result, ok, err, NotFoundError, ConflictError, BusinessError } from '@/types/result.types';
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from '@/lib/mappers/proveedor.mapper';

export class ProveedorService {

    async getAll(empresaId: string): Promise<Result<ProveedorResponse[], BusinessError>> {
        try {
            const entities = await prisma.proveedor.findMany({
                where: { empresa_id: empresaId, activo: true },
                orderBy: { nombre: 'asc' }
            });
            return ok(entities.map(mapEntityToResponse));
        } catch (error) {
            return err(new BusinessError('Error buscando proveedores', 'QUERY_ERROR', 500));
        }
    }

    async getById(empresaId: string, id: ProveedorId): Promise<Result<ProveedorResponse, NotFoundError>> {
        const entity = await prisma.proveedor.findUnique({
            where: { id }
        });

        if (!entity || entity.empresa_id !== empresaId) {
            return err(new NotFoundError('Proveedor', id));
        }

        return ok(mapEntityToResponse(entity));
    }

    async create(empresaId: string, dto: CreateProveedorDTO): Promise<Result<ProveedorResponse, ConflictError | BusinessError>> {
        // Validar Duplicidad de RUC si existe
        if (dto.ruc) {
            const exists = await prisma.proveedor.findFirst({
                where: { ruc: dto.ruc, empresa_id: empresaId }
            });
            // Si existe y es la misma empresa (implícito por query), error.
            if (exists) return err(new ConflictError(`El RUC ${dto.ruc} ya está registrado`));
        }

        try {
            const input = mapDtoToPrismaCreate(dto);
            const createData = {
                ...input,
                empresa: { connect: { id: empresaId } }
            };

            const entity = await prisma.proveedor.create({
                data: createData as any
            });
            return ok(mapEntityToResponse(entity));
        } catch (error: any) {
            if (error.code === 'P2002') return err(new ConflictError('Ya existe un proveedor con estos datos'));
            return err(new BusinessError('Error creando proveedor', 'CREATE_ERROR', 500));
        }
    }

    async update(empresaId: string, id: ProveedorId, dto: UpdateProveedorDTO): Promise<Result<ProveedorResponse, NotFoundError | BusinessError>> {
        const existing = await prisma.proveedor.findUnique({ where: { id } });
        if (!existing || existing.empresa_id !== empresaId) {
            return err(new NotFoundError('Proveedor', id));
        }

        try {
            const input = mapDtoToPrismaUpdate(dto);
            const updated = await prisma.proveedor.update({
                where: { id },
                data: input as any
            });
            return ok(mapEntityToResponse(updated));
        } catch (error) {
            return err(new BusinessError('Error actualizando proveedor', 'UPDATE_ERROR', 500));
        }
    }

    async delete(empresaId: string, id: ProveedorId): Promise<Result<void, BusinessError | NotFoundError>> {
        return (await this.update(empresaId, id, { activo: false })).success ? ok(undefined) : err(new BusinessError('Error eliminando', 'DELETE', 500));
    }
}
