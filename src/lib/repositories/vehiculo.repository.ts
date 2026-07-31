import { Vehiculo, Prisma } from '@prisma/client';
import { BaseRepository } from './base.repository';
import { CreateVehiculoDTO, UpdateVehiculoDTO, VehiculoEntity, VehiculoFilters } from '@/types/domain/vehiculo.types';

export class VehiculoRepository extends BaseRepository<Vehiculo, CreateVehiculoDTO, UpdateVehiculoDTO> {
    protected model = this.db.vehiculo;

    /**
     * Busca un vehículo por su placa única
     */
    /**
     * Busca un vehículo por su placa única
     */
    async findByPlaca(placa: string): Promise<VehiculoEntity | null> {
        try {
            const result = await this.model.findUnique({
                where: { placa },
                include: {
                    tipo_vehiculo: true,
                    neumaticos_instalados: {
                        include: {
                            modelo: { include: { fabricante: true } },
                            ubicacion_posicion: true
                        }
                    }
                }
            });
            return result as VehiculoEntity | null;
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene vehículos con filtros y relaciones
     */
    async findAllWithRelations(filters: VehiculoFilters = {}): Promise<VehiculoEntity[]> {
        const where: Prisma.VehiculoWhereInput = {};

        if (filters.placa) {
            where.placa = { contains: filters.placa, mode: 'insensitive' };
        }
        if (filters.tipo_vehiculo_id) {
            where.tipo_vehiculo_id = filters.tipo_vehiculo_id;
        }
        if (filters.marca) {
            where.marca = { contains: filters.marca, mode: 'insensitive' };
        }
        if (filters.activo !== undefined) {
            where.activo = filters.activo;
        }
        if (filters.empresa_id) {
            where.empresa_id = filters.empresa_id;
        }

        try {
            const result = await this.model.findMany({
                where,
                take: 100,
                include: {
                    tipo_vehiculo: true,
                    neumaticos_instalados: {
                        include: {
                            modelo: { include: { fabricante: true } },
                            ubicacion_posicion: true
                        }
                    }
                },
                orderBy: {
                    placa: 'asc'
                }
            });
            return result as VehiculoEntity[];
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene un vehículo con toda su configuración de ejes y neumáticos
     */
    async findByIdWithFullConfig(id: string): Promise<VehiculoEntity | null> {
        try {
            const result = await this.model.findUnique({
                where: { id },
                include: {
                    tipo_vehiculo: {
                        include: {
                            configuraciones: {
                                include: {
                                    posiciones: true
                                },
                                orderBy: {
                                    numero_eje: 'asc'
                                }
                            }
                        }
                    },
                    neumaticos_instalados: {
                        include: {
                            ubicacion_posicion: true,
                            modelo: {
                                include: {
                                    fabricante: true
                                }
                            }
                        }
                    }
                }
            });
            return result as unknown as VehiculoEntity | null;
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene un vehículo por ID con todas las relaciones para VehiculoEntity.
     * Incluye tipo_vehiculo, neumaticos con modelo y fabricante.
     */
    async findByIdWithFullRelations(id: string): Promise<VehiculoEntity | null> {
        try {
            const result = await this.model.findUnique({
                where: { id },
                include: {
                    tipo_vehiculo: true,
                    neumaticos_instalados: {
                        include: {
                            ubicacion_posicion: true,
                            modelo: {
                                include: {
                                    fabricante: true
                                }
                            }
                        }
                    }
                }
            });
            return result as VehiculoEntity | null;
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }
}
