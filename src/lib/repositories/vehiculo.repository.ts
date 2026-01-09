import { Vehiculo, Prisma } from '@prisma/client';
import { BaseRepository } from './base.repository';
import { CreateVehiculoDTO, UpdateVehiculoDTO, IVehiculo, VehiculoFilters } from '@/types/domain/vehiculo.types';

export class VehiculoRepository extends BaseRepository<Vehiculo, CreateVehiculoDTO, UpdateVehiculoDTO> {
    protected model = this.db.vehiculo;

    /**
     * Busca un vehículo por su placa única
     */
    async findByPlaca(placa: string): Promise<IVehiculo | null> {
        try {
            return await this.model.findUnique({
                where: { placa },
                include: {
                    tipo_vehiculo: true,
                    neumaticos_instalados: {
                        include: {
                            ubicacion_posicion: true
                        }
                    }
                }
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene vehículos con filtros y relaciones
     */
    async findAllWithRelations(filters: VehiculoFilters = {}): Promise<IVehiculo[]> {
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

        try {
            return await this.model.findMany({
                where,
                include: {
                    tipo_vehiculo: true,
                    // No traemos neumáticos en la lista masiva por performance, solo en detalle
                },
                orderBy: {
                    placa: 'asc'
                }
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene un vehículo con toda su configuración de ejes y neumáticos
     */
    async findByIdWithFullConfig(id: string): Promise<IVehiculo | null> {
        try {
            return await this.model.findUnique({
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
                            modelo: true
                        }
                    }
                }
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Obtiene un vehículo por ID con todas las relaciones para VehiculoEntity.
     * Incluye tipo_vehiculo, neumaticos con modelo y fabricante.
     */
    async findByIdWithFullRelations(id: string): Promise<IVehiculo | null> {
        try {
            return await this.model.findUnique({
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
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }
}
