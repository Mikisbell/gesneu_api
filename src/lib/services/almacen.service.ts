import { AlmacenRepository } from '@/lib/repositories/almacen.repository';
import { CreateAlmacenDTO, UpdateAlmacenDTO, AlmacenResponse } from '@/types/domain/almacen.types';
import { AlmacenId } from '@/types/branded.types';
import { Result, ok, err, NotFoundError, ConflictError, BusinessError } from '@/types/result.types';
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from '@/lib/mappers/almacen.mapper';
import { canDeactivateAlmacen } from '@/lib/validators/domain-rules/almacen.rules';
import { prisma } from '@/lib/prisma';

export class AlmacenService {
    private repository: AlmacenRepository;

    constructor() {
        this.repository = new AlmacenRepository();
    }

    async getAll(empresaId: string): Promise<Result<AlmacenResponse[], BusinessError>> {
        try {
            // Filtrar por empresa del usuario autenticado
            const entities = await this.repository.findAll({
                where: { empresa_id: empresaId, activo: true } // RNF10: Listar solo activos por defecto
            });
            const responses = entities.map(mapEntityToResponse);
            return ok(responses);
        } catch (error) {
            return err(new BusinessError('Error finding almacenes', 'QUERY_ERROR', 500));
        }
    }

    async getById(empresaId: string, id: AlmacenId): Promise<Result<AlmacenResponse, NotFoundError>> {
        const entity = await this.repository.findById(id);
        if (!entity) return err(new NotFoundError('Almacén', id));
        // Validar tenant (seguridad)
        if (entity.empresa_id !== empresaId) return err(new NotFoundError('Almacén', id));

        return ok(mapEntityToResponse(entity));
    }

    async create(empresaId: string, dto: CreateAlmacenDTO): Promise<Result<AlmacenResponse, ConflictError | BusinessError>> {
        const existing = await this.repository.findByCodigo(dto.codigo);
        if (existing && existing.empresa_id === empresaId) {
            return err(new ConflictError(`Código ${dto.codigo} ya existe`));
        }

        try {
            const input = mapDtoToPrismaCreate(dto);
            const createData = {
                ...input,
                empresa: { connect: { id: empresaId } }
            };

            const entity = await this.repository.create(createData as any);
            return ok(mapEntityToResponse(entity));
        } catch (error: any) {
            if (error.code === 'P2002') return err(new ConflictError('Almacén duplicado'));
            return err(new BusinessError('Error creando almacén', 'CREATE_ERROR', 500));
        }
    }

    async update(empresaId: string, id: AlmacenId, dto: UpdateAlmacenDTO): Promise<Result<AlmacenResponse, NotFoundError | BusinessError>> {
        const existing = await this.repository.findById(id);
        if (!existing || existing.empresa_id !== empresaId) return err(new NotFoundError('Almacén', id));

        // Validación de desactivación (RF57)
        if (dto.activo === false && existing.activo) {
            const tireCount = await prisma.neumatico.count({
                where: { ubicacion_almacen_id: id, activo: true }
            });
            const canDeactivate = canDeactivateAlmacen(existing, tireCount);
            if (!canDeactivate.success) return err(canDeactivate.error);
        }

        try {
            const input = mapDtoToPrismaUpdate(dto);
            const updated = await this.repository.update(id, input as any);
            return ok(mapEntityToResponse(updated));
        } catch (error) {
            return err(new BusinessError('Error actualizando almacén', 'UPDATE_ERROR', 500));
        }
    }

    async delete(empresaId: string, id: AlmacenId): Promise<Result<void, BusinessError | NotFoundError>> {
        // RNF10: Soft Delete via update
        const result = await this.update(empresaId, id, { activo: false });
        if (!result.success) return err(result.error);
        return ok(undefined);
    }
}
