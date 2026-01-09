import { prisma } from '@/lib/prisma';
import { Prisma } from '@prisma/client';
import { EventoNeumaticoEntity } from '@/types/domain/evento-neumatico.types';
import { EventoId, NeumaticoId, VehiculoId } from '@/types/branded.types';

export class EventoNeumaticoRepository {
    private includeConfig = {
        neumatico: {
            include: {
                modelo: {
                    include: {
                        fabricante: true
                    }
                }
            }
        },
        vehiculo: true,
        posicion_montaje: true,
        almacen_destino: true,
        proveedor: true,
        motivo_desecho: true,
        usuario: true
    } satisfies Prisma.EventoNeumaticoInclude;

    /**
     * Crea un evento transaccional.
     * @param data Datos de creación de Prisma
     * @param tx Cliente de transacción opcional
     */
    async create(
        data: Prisma.EventoNeumaticoCreateInput,
        tx: Prisma.TransactionClient = prisma
    ): Promise<EventoNeumaticoEntity> {
        return tx.eventoNeumatico.create({
            data,
            include: this.includeConfig
        });
    }

    /**
     * Busca un evento por su ID.
     */
    async findById(id: EventoId): Promise<EventoNeumaticoEntity | null> {
        return prisma.eventoNeumatico.findUnique({
            where: { id },
            include: this.includeConfig
        });
    }

    /**
     * Obtiene el historial completo de un neumático.
     */
    async findByNeumaticoId(neumaticoId: NeumaticoId): Promise<EventoNeumaticoEntity[]> {
        return prisma.eventoNeumatico.findMany({
            where: { neumatico_id: neumaticoId },
            orderBy: { fecha_evento: 'desc' },
            include: this.includeConfig
        });
    }

    /**
     * Obtiene los últimos eventos asociados a un vehículo.
     */
    async findRecentByVehiculo(vehiculoId: VehiculoId, limit: number = 10): Promise<EventoNeumaticoEntity[]> {
        return prisma.eventoNeumatico.findMany({
            where: { vehiculo_id: vehiculoId },
            orderBy: { fecha_evento: 'desc' },
            take: limit,
            include: this.includeConfig
        });
    }
}
