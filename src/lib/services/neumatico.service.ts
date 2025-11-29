import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, INeumatico, NeumaticoFilters } from '@/types/domain/neumatico.types';
import { prisma } from '@/lib/prisma';

export class NeumaticoService {
    private repository: NeumaticoRepository;

    constructor() {
        this.repository = new NeumaticoRepository();
    }

    async getAll(filters?: NeumaticoFilters): Promise<INeumatico[]> {
        return await this.repository.findAllWithRelations(filters);
    }

    async getById(id: string): Promise<INeumatico | null> {
        return await this.repository.findById(id);
    }

    async getBySerie(serie: string): Promise<INeumatico | null> {
        return await this.repository.findBySerie(serie);
    }

    async create(data: CreateNeumaticoDTO): Promise<INeumatico> {
        // Validación de negocio: Verificar unicidad de serie
        const existing = await this.repository.findBySerie(data.numero_serie);
        if (existing) {
            throw new Error(`El neumático con serie ${data.numero_serie} ya existe.`);
        }

        return await this.repository.create(data);
    }

    async update(id: string, data: UpdateNeumaticoDTO): Promise<INeumatico> {
        const existing = await this.repository.findById(id);
        if (!existing) {
            throw new Error('Neumático no encontrado');
        }
        return await this.repository.update(id, data);
    }

    async delete(id: string): Promise<INeumatico> {
        return await this.repository.delete(id);
    }

    /**
     * Centralized method to register any tire event.
     * Dispatches to specific handlers based on event type.
     */
    async registrarEvento(evento: any, userId: string): Promise<any> {
        const { tipo_evento } = evento;

        // Start transaction
        return await prisma.$transaction(async (tx) => {
            let result;

            switch (tipo_evento) {
                case 'INSTALACION':
                    result = await this._handleInstalacion(evento, userId, tx);
                    break;
                // Add other cases here as they are implemented
                default:
                    throw new Error(`Evento ${tipo_evento} no soportado aún.`);
            }

            return result;
        });
    }

    private async _handleInstalacion(evento: any, userId: string, tx: any) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date();

        // 1. Validate Tire
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { modelo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (!neumatico.activo) throw new Error('Neumático no está activo');
        if (neumatico.estado_actual !== 'EN_STOCK') throw new Error(`Neumático no está disponible. Estado actual: ${neumatico.estado_actual}`);

        // 2. Validate Vehicle
        const vehiculo = await tx.vehiculo.findUnique({
            where: { id: vehiculo_id }
        });
        if (!vehiculo) throw new Error('Vehículo no encontrado');

        // 3. Validate Position (if provided)
        if (posicion_montaje_id) {
            const posicionOcupada = await tx.neumatico.findFirst({
                where: {
                    ubicacion_posicion_id: posicion_montaje_id,
                    activo: true,
                    estado_actual: 'INSTALADO',
                },
            });
            if (posicionOcupada) throw new Error('La posición especificada ya está ocupada');

            // Validate retread restriction (RF16)
            if (neumatico.es_reencauchado) {
                const posicion = await tx.posicionNeumatico.findUnique({
                    where: { id: posicion_montaje_id },
                    include: { configuracion_eje: true }
                });

                if (posicion && !posicion.configuracion_eje.permite_reencauchados) {
                    throw new Error('Esta posición no permite neumáticos reencauchados');
                }
            }
        }

        // 4. Create Event
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'INSTALACION',
                neumatico_id,
                fecha_evento: now,
                kilometraje_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id,
                posicion_montaje_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        // 5. Update Tire
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: 'INSTALADO',
                ubicacion_almacen_id: null,
                ubicacion_vehiculo_id: vehiculo_id,
                ubicacion_posicion_id: posicion_montaje_id || null,
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                fecha_instalacion: now,
                actualizado_en: now,
            },
        });

        // 6. Create Measurement Log
        if (profundidad_remanente) {
            await tx.medicionProfundidad.create({
                data: {
                    neumatico_id,
                    profundidad_mm: profundidad_remanente,
                    fecha_medicion: now,
                    medido_por: userId,
                },
            });
        }

        // 7. Update Odometer
        if (kilometraje_vehiculo) {
            await tx.registroOdometro.create({
                data: {
                    vehiculo_id,
                    kilometraje: kilometraje_vehiculo,
                    fecha_registro: now,
                    registrado_por: userId,
                    notas: `Montaje de neumático ${neumatico.numero_serie}`,
                },
            });
        }

        // Update Vehicle current mileage if greater
        if (kilometraje_vehiculo && (!vehiculo.kilometraje_actual || kilometraje_vehiculo > vehiculo.kilometraje_actual)) {
            await tx.vehiculo.update({
                where: { id: vehiculo_id },
                data: { kilometraje_actual: kilometraje_vehiculo }
            });
        }

        return nuevoEvento;
    }
}
