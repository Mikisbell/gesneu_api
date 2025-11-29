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
                case 'DESMONTAJE':
                    result = await this._handleDesmontaje(evento, userId, tx);
                    break;
                case 'INSPECCION':
                    result = await this._handleInspeccion(evento, userId, tx);
                    break;
                case 'ROTACION':
                    result = await this._handleRotacion(evento, userId, tx);
                    break;
                case 'REPARACION_ENTRADA':
                    result = await this._handleReparacionEntrada(evento, userId, tx);
                    break;
                case 'REPARACION_SALIDA':
                    result = await this._handleReparacionSalida(evento, userId, tx);
                    break;
                case 'REENCAUCHE_ENTRADA':
                    result = await this._handleReencaucheEntrada(evento, userId, tx);
                    break;
                case 'REENCAUCHE_SALIDA':
                    result = await this._handleReencaucheSalida(evento, userId, tx);
                    break;
                case 'DESECHO':
                    result = await this._handleDesecho(evento, userId, tx);
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
            // Validation: Position must belong to the vehicle type
            const posicion = await tx.posicionNeumatico.findUnique({
                where: { id: posicion_montaje_id },
                include: { configuracion_eje: true }
            });

            if (!posicion) throw new Error('Posición no válida');
            if (posicion.configuracion_eje.tipo_vehiculo_id !== vehiculo.tipo_vehiculo_id) {
                throw new Error('La posición no corresponde al tipo de vehículo');
            }

            const posicionOcupada = await tx.neumatico.findFirst({
                where: {
                    ubicacion_posicion_id: posicion_montaje_id,
                    activo: true,
                    estado_actual: 'INSTALADO',
                },
            });
            if (posicionOcupada) throw new Error(`La posición ya está ocupada por el neumático ${posicionOcupada.numero_serie}`);

            // Validate retread restriction (RF16)
            if (neumatico.es_reencauchado && !posicion.configuracion_eje.permite_reencauchados) {
                throw new Error('Esta posición no permite neumáticos reencauchados');
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

        // 5b. Create History Record
        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: 'INSTALADO',
                fecha_cambio: now,
                motivo: `Montaje en vehículo ${vehiculo.placa}`
            }
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

    private async _handleDesmontaje(evento: any, userId: string, tx: any) {
        const { neumatico_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones, estado_neumatico_resultante, almacen_destino_id, motivo_desecho_id } = evento;
        const now = new Date();

        // 1. Validate Tire
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { ubicacion_vehiculo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (neumatico.estado_actual !== 'INSTALADO') throw new Error(`El neumático no está instalado. Estado actual: ${neumatico.estado_actual}`);

        // 2. Calculate accumulated mileage
        let kmRecorrido = 0;
        if (neumatico.fecha_instalacion && kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            // Get vehicle to check previous mileage or use installation mileage if stored (ideally should be stored in tire or event)
            // For simplicity, we assume we can calculate diff if we had km_instalacion. 
            // Since Neumatico model doesn't have km_instalacion explicitly in the provided schema snippet (it might be in event),
            // we will rely on the requirement RF19: Update kilometraje_acumulado.
            // We need the installation event to know km at installation.
            const instalacionEvento = await tx.eventoNeumatico.findFirst({
                where: {
                    neumatico_id: neumatico_id,
                    tipo_evento: 'INSTALACION',
                },
                orderBy: { fecha_evento: 'desc' }
            });

            if (instalacionEvento && instalacionEvento.kilometraje_vehiculo) {
                kmRecorrido = kilometraje_vehiculo - instalacionEvento.kilometraje_vehiculo;
                if (kmRecorrido < 0) kmRecorrido = 0; // Safety check
            }
        }

        // 3. Create Event
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'DESMONTAJE',
                neumatico_id,
                fecha_evento: now,
                kilometraje_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id: neumatico.ubicacion_vehiculo_id, // Record where it came from
                posicion_montaje_id: neumatico.ubicacion_posicion_id,
                almacen_destino_id,
                motivo_desecho_id, // Add if present
                notas: observaciones,
                creado_por: userId,
            },
        });

        // 4. Update Tire
        const nuevoEstado = estado_neumatico_resultante || 'EN_STOCK';

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: nuevoEstado,
                ubicacion_almacen_id: almacen_destino_id || null, // Should be provided if going to stock
                ubicacion_vehiculo_id: null,
                ubicacion_posicion_id: null,
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                kilometraje_acumulado: { increment: kmRecorrido },
                fecha_desecho: nuevoEstado === 'DESECHADO' ? now : null,
                actualizado_en: now,
            },
        });

        // 4b. Create History Record
        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: nuevoEstado,
                fecha_cambio: now,
                motivo: `Desmontaje de vehículo ${neumatico.ubicacion_vehiculo?.placa || 'Desconocido'}`
            }
        });

        // 5. Create Measurement Log
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

        // 6. Update Vehicle Odometer
        if (kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await tx.registroOdometro.create({
                data: {
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    kilometraje: kilometraje_vehiculo,
                    fecha_registro: now,
                    registrado_por: userId,
                    notas: `Desmontaje de neumático ${neumatico.numero_serie}`,
                },
            });

            // Update vehicle current km
            await tx.vehiculo.update({
                where: { id: neumatico.ubicacion_vehiculo_id },
                data: { kilometraje_actual: kilometraje_vehiculo }
            });
        }

        return nuevoEvento;
    }

    private async _handleInspeccion(evento: any, userId: string, tx: any) {
        const { neumatico_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date();

        // 1. Validate Tire
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { modelo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (!neumatico.activo) throw new Error('Neumático no está activo');

        // 2. Create Event
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'INSPECCION',
                neumatico_id,
                fecha_evento: now,
                kilometraje_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id: neumatico.ubicacion_vehiculo_id,
                posicion_montaje_id: neumatico.ubicacion_posicion_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        // 3. Update Tire
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                actualizado_en: now,
            },
        });

        // 4. Create Measurement Log
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

        // 5. Update Odometer (if attached to vehicle)
        if (kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await tx.registroOdometro.create({
                data: {
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    kilometraje: kilometraje_vehiculo,
                    fecha_registro: now,
                    registrado_por: userId,
                    notas: `Inspección de neumático ${neumatico.numero_serie}`,
                },
            });

            // Update vehicle current km
            await tx.vehiculo.update({
                where: { id: neumatico.ubicacion_vehiculo_id },
                data: { kilometraje_actual: kilometraje_vehiculo }
            });
        }

        // 6. Check Alerts (Simplified Logic for now)
        // In a real scenario, this would call AlertService
        if (profundidad_remanente && neumatico.modelo?.profundidad_minima_recomendada_mm) {
            if (profundidad_remanente <= Number(neumatico.modelo.profundidad_minima_recomendada_mm)) {
                // Create Alert
                await tx.alerta.create({
                    data: {
                        tipo_alerta: 'PROFUNDIDAD_BAJA',
                        mensaje: `Neumático ${neumatico.numero_serie} con profundidad baja (${profundidad_remanente}mm)`,
                        nivel_severidad: 'WARN',
                        estado_alerta: 'NUEVA',
                        neumatico_id: neumatico.id,
                        vehiculo_id: neumatico.ubicacion_vehiculo_id,
                        almacen_id: neumatico.ubicacion_almacen_id,
                    }
                });
            }
        }

        return nuevoEvento;
    }

    private async _handleRotacion(evento: any, userId: string, tx: any) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date();

        // 1. Validate Primary Tire (Tire A)
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { modelo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (neumatico.estado_actual !== 'INSTALADO') throw new Error('El neumático debe estar INSTALADO para rotarse');
        if (!neumatico.ubicacion_vehiculo_id) throw new Error('El neumático no está asignado a ningún vehículo');

        const currentPosId = neumatico.ubicacion_posicion_id;
        const targetPosId = posicion_montaje_id;

        if (!targetPosId) throw new Error('Debe especificar la posición de destino para la rotación');
        if (currentPosId === targetPosId) throw new Error('La posición de destino es la misma que la actual');

        // 2. Validate Target Position
        // Check if there is a tire in the target position (Tire B)
        const neumaticoEnDestino = await tx.neumatico.findFirst({
            where: {
                ubicacion_posicion_id: targetPosId,
                activo: true,
                estado_actual: 'INSTALADO',
                // Ensure it's on the same vehicle if we assume intra-vehicle rotation
                ubicacion_vehiculo_id: neumatico.ubicacion_vehiculo_id
            }
        });

        // 3. Create Event for Tire A
        const eventoRotacion = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'ROTACION',
                neumatico_id,
                fecha_evento: now,
                kilometraje_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id: neumatico.ubicacion_vehiculo_id,
                posicion_montaje_id: targetPosId, // New position
                notas: observaciones,
                creado_por: userId,
            },
        });

        // 4. Update Tire A
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                ubicacion_posicion_id: targetPosId,
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                actualizado_en: now,
            },
        });

        // 5. Handle Swap (if Tire B exists)
        if (neumaticoEnDestino) {
            // Create Event for Tire B (Swap)
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: 'ROTACION',
                    neumatico_id: neumaticoEnDestino.id,
                    fecha_evento: now,
                    kilometraje_vehiculo, // Same mileage
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    posicion_montaje_id: currentPosId, // Moves to A's old position
                    notas: `Rotación automática (intercambio con ${neumatico.numero_serie})`,
                    creado_por: userId,
                },
            });

            // Update Tire B
            await tx.neumatico.update({
                where: { id: neumaticoEnDestino.id },
                data: {
                    ubicacion_posicion_id: currentPosId,
                    actualizado_en: now,
                },
            });
        }

        // 6. Update Odometer (once per operation)
        if (kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await tx.registroOdometro.create({
                data: {
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    kilometraje: kilometraje_vehiculo,
                    fecha_registro: now,
                    registrado_por: userId,
                    notas: `Rotación de neumáticos`,
                },
            });

            await tx.vehiculo.update({
                where: { id: neumatico.ubicacion_vehiculo_id },
                data: { kilometraje_actual: kilometraje_vehiculo }
            });
        }

        return eventoRotacion;
    }

    private async _handleReparacionEntrada(evento: any, userId: string, tx: any) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date();

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');

        // Allow sending from STOCK or PARA_REPARACION
        const validStates = ['EN_STOCK', 'PARA_REPARACION', 'INSTALADO']; // If INSTALADO, should use DESMONTAJE first, but maybe we allow direct? No, stick to flow.
        // Actually, if it's INSTALADO, it must be dismounted first.
        if (!['EN_STOCK', 'PARA_REPARACION'].includes(neumatico.estado_actual)) {
            throw new Error(`El neumático debe estar EN_STOCK o PARA_REPARACION. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'REPARACION_ENTRADA',
                neumatico_id,
                fecha_evento: now,
                proveedor_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: 'EN_REPARACION',
                ubicacion_almacen_id: null, // It's at the provider
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: 'EN_REPARACION',
                fecha_cambio: now,
                motivo: `Envío a reparación`
            }
        });

        return nuevoEvento;
    }

    private async _handleReparacionSalida(evento: any, userId: string, tx: any) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date();

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');
        if (neumatico.estado_actual !== 'EN_REPARACION') {
            throw new Error(`El neumático no está en reparación. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'REPARACION_SALIDA',
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: 'EN_STOCK', // Back to stock
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_actual_mm: profundidad_remanente || undefined,
                reparaciones_cantidad: { increment: 1 },
                costo_total_reparaciones: costo_evento ? { increment: costo_evento } : undefined,
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: 'EN_STOCK',
                fecha_cambio: now,
                motivo: `Retorno de reparación`
            }
        });

        return nuevoEvento;
    }

    private async _handleReencaucheEntrada(evento: any, userId: string, tx: any) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date();

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');

        if (!['EN_STOCK', 'PARA_REENCAUCHE'].includes(neumatico.estado_actual)) {
            throw new Error(`El neumático debe estar EN_STOCK o PARA_REENCAUCHE. Estado actual: ${neumatico.estado_actual}`);
        }

        // Validate max retreads (RF16)
        if (neumatico.cantidad_reencauches >= neumatico.maximo_reencauches) {
            throw new Error(`El neumático ha alcanzado el límite de reencauches (${neumatico.maximo_reencauches})`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'REENCAUCHE_ENTRADA',
                neumatico_id,
                fecha_evento: now,
                proveedor_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: 'EN_REENCAUCHE',
                ubicacion_almacen_id: null,
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: 'EN_REENCAUCHE',
                fecha_cambio: now,
                motivo: `Envío a reencauche`
            }
        });

        return nuevoEvento;
    }

    private async _handleReencaucheSalida(evento: any, userId: string, tx: any) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date();

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');
        if (neumatico.estado_actual !== 'EN_REENCAUCHE') {
            throw new Error(`El neumático no está en reencauche. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'REENCAUCHE_SALIDA',
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: 'EN_STOCK',
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_actual_mm: profundidad_remanente || undefined,
                es_reencauchado: true,
                cantidad_reencauches: { increment: 1 },
                costo_total_reencauches: costo_evento ? { increment: costo_evento } : undefined,
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: 'EN_STOCK',
                fecha_cambio: now,
                motivo: `Retorno de reencauche`
            }
        });

        return nuevoEvento;
    }

    private async _handleDesecho(evento: any, userId: string, tx: any) {
        const { neumatico_id, motivo_desecho_id, observaciones } = evento;
        const now = new Date();

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');

        // Can be discarded from almost any state except installed (should be dismounted first)
        if (neumatico.estado_actual === 'INSTALADO') {
            throw new Error('El neumático debe ser desmontado antes de desecharse');
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'DESECHO',
                neumatico_id,
                fecha_evento: now,
                motivo_desecho_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: 'DESECHADO',
                ubicacion_almacen_id: null,
                ubicacion_vehiculo_id: null,
                ubicacion_posicion_id: null,
                fecha_desecho: now,
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: 'DESECHADO',
                fecha_cambio: now,
                motivo: `Baja definitiva`
            }
        });

        return nuevoEvento;
    }
}
