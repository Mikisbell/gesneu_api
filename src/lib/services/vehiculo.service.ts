/**
 * VehiculoService - Capa de Servicio Profesional
 * 
 * Este servicio implementa la lógica de negocio para la entidad Vehiculo
 * siguiendo los patrones de tipado profesional:
 * - Result Types para manejo explícito de errores
 * - Mappers para transformación entre capas
 * - Branded IDs para seguridad de tipos
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { VehiculoRepository } from '@/lib/repositories/vehiculo.repository';
import {
    CreateVehiculoDTO,
    UpdateVehiculoDTO,
    VehiculoResponse,
    VehiculoListItem,
    VehiculoFilters,
    IVehiculo,
} from '@/types/domain/vehiculo.types';
import { VehiculoId } from '@/types/branded.types';
import {
    Result,
    ok,
    err,
    NotFoundError,
    ConflictError,
    BusinessError,
} from '@/types/result.types';
import {
    mapDtoToPrismaCreate,
    mapDtoToPrismaUpdate,
    mapEntityToResponse,
    mapEntitiesToListItems,
} from '@/lib/mappers/vehiculo.mapper';
import { canDeleteVehiculo } from '@/lib/validators/domain-rules/vehiculo.rules';

/**
 * Servicio para gestión de Vehículos.
 * Implementa lógica de negocio y validaciones.
 */
export class VehiculoService {
    private repository: VehiculoRepository;

    constructor() {
        this.repository = new VehiculoRepository();
    }

    // ============================================
    // QUERIES (Lectura)
    // ============================================

    /**
     * Obtiene todos los vehículos con filtros opcionales.
     * @returns Lista de vehículos formateados para listado
     */
    async getAll(filters?: VehiculoFilters): Promise<Result<VehiculoListItem[], BusinessError>> {
        try {
            const entities = await this.repository.findAllWithRelations(filters);
            const listItems = mapEntitiesToListItems(entities as any);
            return ok(listItems);
        } catch (error) {
            return err(new BusinessError(
                'Error al obtener vehículos',
                'QUERY_ERROR',
                500
            ));
        }
    }

    /**
     * Obtiene un vehículo por su ID.
     * @param id - ID tipado del vehículo
     * @returns Response del vehículo o error NotFound
     */
    async getById(id: VehiculoId): Promise<Result<VehiculoResponse, NotFoundError>> {
        const entity = await this.repository.findByIdWithFullRelations(id);

        if (!entity) {
            return err(new NotFoundError('Vehículo', id));
        }

        const response = mapEntityToResponse(entity as any);
        return ok(response);
    }

    /**
     * Obtiene un vehículo por ID con configuración completa.
     * Incluye todas las relaciones anidadas.
     */
    async getByIdWithFullConfig(id: VehiculoId): Promise<Result<VehiculoResponse, NotFoundError>> {
        const entity = await this.repository.findByIdWithFullConfig(id);

        if (!entity) {
            return err(new NotFoundError('Vehículo', id));
        }

        const response = mapEntityToResponse(entity as any);
        return ok(response);
    }

    /**
     * Busca un vehículo por placa.
     * @param placa - Placa del vehículo
     */
    async getByPlaca(placa: string): Promise<Result<VehiculoResponse, NotFoundError>> {
        const entity = await this.repository.findByPlaca(placa);

        if (!entity) {
            return err(new NotFoundError('Vehículo con placa ' + placa));
        }

        const response = mapEntityToResponse(entity as any);
        return ok(response);
    }

    // ============================================
    // COMMANDS (Escritura)
    // ============================================

    /**
     * Crea un nuevo vehículo.
     * @param dto - Datos del vehículo a crear
     * @param empresa_id - ID de la empresa (multi-tenancy)
     * @returns Response del vehículo creado o error de conflicto
     */
    async create(
        dto: CreateVehiculoDTO,
        empresa_id: string
    ): Promise<Result<VehiculoResponse, ConflictError | BusinessError>> {
        // Validación de negocio: Verificar unicidad de placa
        const existing = await this.repository.findByPlaca(dto.placa);
        if (existing) {
            return err(new ConflictError(`Ya existe un vehículo con placa ${dto.placa}`));
        }

        try {
            // Transformar DTO a input de Prisma usando mapper
            const prismaInput = mapDtoToPrismaCreate(dto);

            // Agregar empresa_id al input (requerido para multi-tenancy)
            const createData = {
                ...prismaInput,
                empresa: { connect: { id: empresa_id } },
            };

            // Crear en base de datos
            const entity = await this.repository.create(createData as any);

            // Transformar entity a response
            const response = mapEntityToResponse(entity as any);

            return ok(response);
        } catch (error: any) {
            // Manejar errores específicos de Prisma
            if (error.code === 'P2002') {
                return err(new ConflictError('Ya existe un vehículo con esos datos únicos'));
            }

            return err(new BusinessError(
                error.message || 'Error al crear vehículo',
                'CREATE_ERROR',
                500
            ));
        }
    }

    /**
     * Actualiza un vehículo existente.
     * @param id - ID tipado del vehículo
     * @param dto - Datos a actualizar
     * @returns Response del vehículo actualizado o error
     */
    async update(
        id: VehiculoId,
        dto: UpdateVehiculoDTO
    ): Promise<Result<VehiculoResponse, NotFoundError | ConflictError | BusinessError>> {
        // Verificar que existe
        const existing = await this.repository.findById(id);
        if (!existing) {
            return err(new NotFoundError('Vehículo', id));
        }

        // Verificar unicidad de placa si se está cambiando
        if (dto.placa && dto.placa !== existing.placa) {
            const withSamePlaca = await this.repository.findByPlaca(dto.placa);
            if (withSamePlaca && withSamePlaca.id !== id) {
                return err(new ConflictError(`Ya existe otro vehículo con placa ${dto.placa}`));
            }
        }

        try {
            // Transformar DTO a input de Prisma usando mapper
            const prismaInput = mapDtoToPrismaUpdate(dto);

            // Actualizar en base de datos
            const entity = await this.repository.update(id, prismaInput as any);

            // Transformar entity a response
            const response = mapEntityToResponse(entity as any);

            return ok(response);
        } catch (error: any) {
            return err(new BusinessError(
                error.message || 'Error al actualizar vehículo',
                'UPDATE_ERROR',
                500
            ));
        }
    }

    /**
     * Elimina un vehículo.
     * @param id - ID tipado del vehículo
     * @returns Response del vehículo eliminado o error
     */
    async delete(id: VehiculoId): Promise<Result<VehiculoResponse, NotFoundError | BusinessError>> {
        const existing = await this.repository.findById(id);
        if (!existing) {
            return err(new NotFoundError('Vehículo', id));
        }

        // Recuperar con relaciones para validar
        // Es mejor usar findByIdWithFullRelations si necesitamos chequear neumáticos instalados
        // El findById standard podría no traer la relación
        const fullEntity = await this.repository.findByIdWithFullRelations(id);

        if (fullEntity) {
            const canDelete = canDeleteVehiculo(fullEntity);
            if (!canDelete.success) return err(canDelete.error);
        }

        try {
            const entity = await this.repository.delete(id);
            const response = mapEntityToResponse(entity as any);
            return ok(response);
        } catch (error: any) {
            return err(new BusinessError(
                error.message || 'Error al eliminar vehículo',
                'DELETE_ERROR',
                500
            ));
        }
    }

    // ============================================
    // LEGACY METHODS (Para compatibilidad)
    // Estos métodos mantienen la firma antigua para no romper código existente.
    // Se deben migrar gradualmente.
    // ============================================

    /**
     * @deprecated Usar getAll() que devuelve Result<VehiculoListItem[], Error>
     */
    async getAllLegacy(filters?: VehiculoFilters): Promise<IVehiculo[]> {
        return await this.repository.findAllWithRelations(filters);
    }

    /**
     * @deprecated Usar getById(VehiculoId) que devuelve Result<VehiculoResponse, Error>
     */
    async getByIdLegacy(id: string): Promise<IVehiculo | null> {
        return await this.repository.findById(id);
    }

    /**
     * @deprecated Usar create() que devuelve Result<VehiculoResponse, Error>
     */
    async createLegacy(data: CreateVehiculoDTO, empresa_id: string): Promise<IVehiculo> {
        const result = await this.create(data, empresa_id);
        if (!result.success) {
            throw result.error;
        }
        return result.data as any;
    }

    /**
     * @deprecated Usar update() que devuelve Result<VehiculoResponse, Error>
     */
    async updateLegacy(id: string, data: UpdateVehiculoDTO): Promise<IVehiculo> {
        const result = await this.update(id as VehiculoId, data);
        if (!result.success) {
            throw result.error;
        }
        return result.data as any;
    }

    /**
     * @deprecated Usar delete() que devuelve Result<VehiculoResponse, Error>
     */
    async deleteLegacy(id: string): Promise<IVehiculo> {
        const result = await this.delete(id as VehiculoId);
        if (!result.success) {
            throw result.error;
        }
        return result.data as any;
    }
}
