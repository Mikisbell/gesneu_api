import { Neumatico, Prisma } from '@prisma/client';
import { BaseRepository } from './base.repository';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, NeumaticoEntity, NeumaticoFilters } from '@/types/domain/neumatico.types';
import { NeumaticoId } from '@/types/branded.types';

export class NeumaticoRepository extends BaseRepository<Neumatico, CreateNeumaticoDTO, UpdateNeumaticoDTO> {
    protected model = this.db.neumatico;

    /**
     * Busca un neumático por su número de serie único
     */
    async findBySerie(numeroSerie: string): Promise<NeumaticoEntity | null> {
        try {
            return await this.model.findFirst({
                where: { numero_serie: numeroSerie },
                include: {
                    modelo: {
                        include: {
                            fabricante: true
                        }
                    },
                    ubicacion_almacen: true,
                    ubicacion_vehiculo: {
                        include: {
                            tipo_vehiculo: true
                        }
                    },
                    ubicacion_posicion: true,
                    proveedor_compra: true,
                    motivo_desecho: true
                }
            }) as unknown as NeumaticoEntity | null;
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene neumáticos con filtros avanzados y relaciones
     */
    async findAllWithRelations(filters: NeumaticoFilters = {}): Promise<NeumaticoEntity[]> {
        const where: Prisma.NeumaticoWhereInput = {};

        if (filters.search) {
            where.OR = [
                { numero_serie: { contains: filters.search, mode: 'insensitive' } },
                { ubicacion_vehiculo: { placa: { contains: filters.search, mode: 'insensitive' } } }
            ];
        }
        if (filters.numero_serie) {
            where.numero_serie = { contains: filters.numero_serie, mode: 'insensitive' };
        }
        if (filters.modelo_id) {
            where.modelo_id = filters.modelo_id;
        }
        if (filters.estado_actual) {
            where.estado_actual = filters.estado_actual as any;
        }
        if (filters.ubicacion_almacen_id) {
            where.ubicacion_almacen_id = filters.ubicacion_almacen_id;
        }
        if (filters.ubicacion_vehiculo_id) {
            where.ubicacion_vehiculo_id = filters.ubicacion_vehiculo_id;
        }
        if (filters.dot) {
            where.dot = filters.dot;
        }

        try {
            return await this.model.findMany({
                where,
                include: {
                    modelo: {
                        include: {
                            fabricante: true
                        }
                    },
                    ubicacion_almacen: true,
                    ubicacion_vehiculo: {
                        include: {
                            tipo_vehiculo: true
                        }
                    },
                    ubicacion_posicion: true,
                    proveedor_compra: true,
                    motivo_desecho: true
                },
                orderBy: {
                    creado_en: 'desc'
                }
            }) as unknown as NeumaticoEntity[];
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Busca un neumático por ID con todas sus relaciones
     */
    async findByIdWithFullRelations(id: NeumaticoId): Promise<NeumaticoEntity | null> {
        try {
            return await this.model.findUnique({
                where: { id },
                include: {
                    modelo: {
                        include: {
                            fabricante: true
                        }
                    },
                    ubicacion_almacen: true,
                    ubicacion_vehiculo: {
                        include: {
                            tipo_vehiculo: true
                        }
                    },
                    ubicacion_posicion: true,
                    proveedor_compra: true,
                    motivo_desecho: true
                }
            }) as unknown as NeumaticoEntity | null;
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }
}
