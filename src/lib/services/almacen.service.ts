/**
 * AlmacenService - Simple Catalog Service
 */
import { AlmacenRepository } from '@/lib/repositories/almacen.repository';
import { CreateAlmacenDTO, UpdateAlmacenDTO, AlmacenResponse } from '@/types/domain/almacen.types';
import { AlmacenId, EmpresaId } from '@/types/branded.types';
import { Result, ok, err, NotFoundError, ConflictError, BusinessError } from '@/types/result.types';
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from '@/lib/mappers/almacen.mapper';
import { canDeactivateAlmacen } from '@/lib/validators/domain-rules/almacen.rules';
import { prisma } from '@/lib/prisma'; // Accesing prisma directly only for counting tires (optimized)

export class AlmacenService {
    private repository: AlmacenRepository;

    constructor() {
        this.repository = new AlmacenRepository();
    }

    async getAll(empresaId: EmpresaId): Promise<Result<AlmacenResponse[], BusinessError>> {
        try {
            // Catalogs are usually filtered by tenant
            const entities = await this.repository.findAll();
            // TODO: Add tenant filtering to BaseRepository or override findAll
            // For now assuming BaseRepository will support criteria
            const responses = entities.map(mapEntityToResponse);
            return ok(responses);
        } catch (error) {
            return err(new BusinessError('Error finding almacenes', 'QUERY_ERROR', 500));
        }
    }

    async getById(id: AlmacenId): Promise<Result<AlmacenResponse, NotFoundError>> {
        const entity = await this.repository.findById(id);
        if (!entity) return err(new NotFoundError('Almacén', id));
        return ok(mapEntityToResponse(entity));
    }

    async create(dto: CreateAlmacenDTO, empresaId: EmpresaId): Promise<Result<AlmacenResponse, ConflictError | BusinessError>> {
        const existing = await this.repository.findByCodigo(dto.codigo);
        if (existing) return err(new ConflictError(`Código ${dto.codigo} ya existe`));

        try {
            const input = mapDtoToPrismaCreate(dto);
            // Manual tenant injection until Repository handles it seamlessly
            const createData = { ...input, empresa: { connect: { id: empresaId } } };

            const entity = await this.repository.create(createData as any);
            return ok(mapEntityToResponse(entity));
        } catch (error: any) {
            if (error.code === 'P2002') return err(new ConflictError('Almacén duplicado'));
            return err(new BusinessError('Error creando almacén', 'CREATE_ERROR', 500));
        }
    }

    async update(id: AlmacenId, dto: UpdateAlmacenDTO): Promise<Result<AlmacenResponse, NotFoundError | BusinessError>> {
        const existing = await this.repository.findById(id);
        if (!existing) return err(new NotFoundError('Almacén', id));

        // Domain Rule: Deactivation check
        if (dto.activo === false && existing.activo) {
            // Count tires in stock
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

    async delete(id: AlmacenId): Promise<Result<void, BusinessError>> {
        // Usually catalogs are soft-deleted or just deactivated
        // Implementing strict delete for completeness
        try {
            await this.repository.delete(id);
            return ok(undefined);
        } catch (error) {
            return err(new BusinessError('Error eliminando almacén', 'DELETE_ERROR', 500));
        }
    }
}
