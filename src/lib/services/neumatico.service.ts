import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, INeumatico, NeumaticoFilters } from '@/types/domain/neumatico.types';
import { prisma } from '@/lib/prisma';
import { EventoNeumaticoCreate } from '@/lib/validators/evento-neumatico';
import { TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, Prisma } from '@prisma/client';

// Type for Prisma transaction client
type TxClient = Prisma.TransactionClient;

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
    async registrarEvento(evento: EventoNeumaticoCreate, userId: string): Promise<any> {
        const { tipo_evento } = evento;

        // Start transaction
        return await prisma.$transaction(async (tx) => {
            let result;

            switch (tipo_evento) {
                case TipoEventoNeumaticoEnum.INSTALACION:
                    result = await this._handleInstalacion(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.DESMONTAJE:
                    result = await this._handleDesmontaje(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.INSPECCION:
                    result = await this._handleInspeccion(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.ROTACION:
                    result = await this._handleRotacion(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.REPARACION_ENTRADA:
                    result = await this._handleReparacionEntrada(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.REPARACION_SALIDA:
                    result = await this._handleReparacionSalida(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA:
                    result = await this._handleReencaucheEntrada(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA:
                    result = await this._handleReencaucheSalida(evento, userId, tx);
                    break;
                case TipoEventoNeumaticoEnum.DESECHO:
                    result = await this._handleDesecho(evento, userId, tx);
                    break;
                // Add other cases here as they are implemented
                default:
                    throw new Error(`Evento ${tipo_evento} no soportado aún.`);
            }

            return result;
        });
    }

    /**
     * Helper method to validate and fetch a tire with proper error handling.
     * Reduces code duplication across event handlers.
     */
    private async _validateAndGetNeumatico(tx: TxClient, id: string, includes: any = {}) {
        const neumatico = await tx.neumatico.findUnique({
            where: { id },
            include: includes
        });

        if (!neumatico) {
            throw new Error('Neumático no encontrado');
        }

        if (!neumatico.activo) {
            throw new Error('Neumático no está activo');
        }

        return neumatico;
    }

    private async _handleInstalacion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !vehiculo_id) throw new Error('Faltan datos requeridos para instalación');

        // 1. Validate Tire
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { modelo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (!neumatico.activo) throw new Error('Neumático no está activo');
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw new Error(`Neumático no está disponible. Estado actual: ${neumatico.estado_actual}`);

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
                    estado_actual: EstadoNeumaticoEnum.INSTALADO,
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
                tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
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
                estado_actual: EstadoNeumaticoEnum.INSTALADO,
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
                estado_nuevo: EstadoNeumaticoEnum.INSTALADO,
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

    private async _handleDesmontaje(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones, estado_neumatico_resultante, almacen_destino_id, motivo_desecho_id } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para desmontaje');

        // 1. Validate Tire
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { ubicacion_vehiculo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw new Error(`El neumático no está instalado. Estado actual: ${neumatico.estado_actual}`);

        // 2. Calculate accumulated mileage
        let kmRecorrido = 0;
        if (neumatico.fecha_instalacion && kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            const instalacionEvento = await tx.eventoNeumatico.findFirst({
                where: {
                    neumatico_id: neumatico_id,
                    tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                },
                orderBy: { fecha_evento: 'desc' }
            });

            if (instalacionEvento?.kilometraje_vehiculo) {
                kmRecorrido = kilometraje_vehiculo - instalacionEvento.kilometraje_vehiculo;
                // 🚨 CRITICAL FIX: Throw error instead of silently setting to 0
                if (kmRecorrido < 0) {
                    throw new Error(
                        `Kilometraje inválido: El kilometraje actual (${kilometraje_vehiculo}) es menor que ` +
                        `el de la última instalación (${instalacionEvento.kilometraje_vehiculo}). ` +
                        `Verifique el odómetro del vehículo.`
                    );
                }
                await tx.neumatico.update({
                    where: { id: neumatico_id },
                    data: { kilometraje_acumulado: { increment: kmRecorrido } }
                });
            }
        }
        let nuevoEstado = estado_neumatico_resultante || EstadoNeumaticoEnum.EN_STOCK;
        let tipoEvento = TipoEventoNeumaticoEnum.DESMONTAJE;

        // Validation based on destination
        if (nuevoEstado === EstadoNeumaticoEnum.EN_STOCK && !almacen_destino_id) {
            throw new Error('Debe especificar un almacén destino para devolver a stock');
        }
        if (nuevoEstado === EstadoNeumaticoEnum.DESECHADO) {
            if (!motivo_desecho_id) throw new Error('Debe especificar un motivo para el desecho');
            // Note: We keep the event type as DESMONTAJE, but the state becomes DESECHADO. 
            // Alternatively, we could create a secondary DESECHO event, but keeping it simple is better.
            // Requirement says: "Desmontaje" implies taking it off. "Desecho" is the fate.
        }

        // 4. Create Event
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: tipoEvento,
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

        // 5. Update Tire
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
                fecha_desecho: nuevoEstado === EstadoNeumaticoEnum.DESECHADO ? now : null,
                actualizado_en: now,
            },
        });

        // 5b. Create History Record
        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: nuevoEstado,
                fecha_cambio: now,
                motivo: `Desmontaje de vehículo ${neumatico.ubicacion_vehiculo?.placa || 'Desconocido'}`
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

        // 7. Update Vehicle Odometer
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

    private async _handleInspeccion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para inspección');

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
                tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
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
        if (profundidad_remanente && neumatico.modelo?.profundidad_minima_recomendada_mm) {
            if (profundidad_remanente <= Number(neumatico.modelo.profundidad_minima_recomendada_mm)) {
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

    private async _handleRotacion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !posicion_montaje_id) throw new Error('Faltan datos requeridos para rotación');

        // 1. Validate Primary Tire (Tire A)
        const neumatico = await tx.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { modelo: true }
        });

        if (!neumatico) throw new Error('Neumático no encontrado');
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw new Error('El neumático debe estar INSTALADO para rotarse');
        if (!neumatico.ubicacion_vehiculo_id) throw new Error('El neumático no está asignado a ningún vehículo');

        const currentPosId = neumatico.ubicacion_posicion_id;
        const targetPosId = posicion_montaje_id;

        if (currentPosId === targetPosId) throw new Error('La posición de destino es la misma que la actual');

        // 2. Validate Target Position and fetch position details for validation
        const targetPosition = await tx.posicionNeumatico.findUnique({
            where: { id: targetPosId },
            include: { configuracion_eje: true }
        });

        if (!targetPosition) throw new Error('Posición de destino no encontrada');

        // Validate Tire A can go to target position (reencauche check)
        if (neumatico.es_reencauchado && !targetPosition.configuracion_eje.permite_reencauchados) {
            throw new Error('El neumático reencauchado no puede instalarse en esta posición');
        }

        // Check if there is a tire in the target position (Tire B)
        const neumaticoEnDestino = await tx.neumatico.findFirst({
            where: {
                ubicacion_posicion_id: targetPosId,
                activo: true,
                estado_actual: EstadoNeumaticoEnum.INSTALADO,
                // Ensure it's on the same vehicle if we assume intra-vehicle rotation
                ubicacion_vehiculo_id: neumatico.ubicacion_vehiculo_id
            }
        });

        // 🚨 CRITICAL FIX: Bidirectional validation for swap
        if (neumaticoEnDestino && currentPosId) {
            // Fetch origin position details to validate Tire B compatibility
            const originPosition = await tx.posicionNeumatico.findUnique({
                where: { id: currentPosId },
                include: { configuracion_eje: true }
            });

            if (!originPosition) throw new Error('Posición de origen no encontrada');

            // Validate that Tire B can go to origin position (Tire A's old position)
            if (neumaticoEnDestino.es_reencauchado && !originPosition.configuracion_eje.permite_reencauchados) {
                throw new Error(
                    `No se puede realizar el intercambio: El neumático ${neumaticoEnDestino.numero_serie} ` +
                    `(reencauchado) no está permitido en la posición de origen.`
                );
            }
        }

        // 3. Create Event for Tire A
        const eventoRotacion = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
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
        if (neumaticoEnDestino && currentPosId) {
            // Create Event for Tire B (Swap)
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
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

    private async _handleReparacionEntrada(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para reparación');

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');

        // Allow sending from STOCK only
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
            throw new Error(`El neumático debe estar EN_STOCK. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REPARACION_ENTRADA,
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
                estado_actual: EstadoNeumaticoEnum.EN_REPARACION,
                ubicacion_almacen_id: null, // It's at the provider
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: EstadoNeumaticoEnum.EN_REPARACION,
                fecha_cambio: now,
                motivo: `Envío a reparación`
            }
        });

        return nuevoEvento;
    }

    private async _handleReparacionSalida(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para retorno de reparación');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REPARACION) {
            throw new Error(`El neumático no está en reparación. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REPARACION_SALIDA,
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId,
            },
        });

        // Cost tracking fields don't exist in schema - removed
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.EN_STOCK, // Back to stock
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_actual_mm: profundidad_remanente || undefined,
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: EstadoNeumaticoEnum.EN_STOCK,
                fecha_cambio: now,
                motivo: `Retorno de reparación`
            }
        });

        return nuevoEvento;
    }

    private async _handleReencaucheEntrada(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para reencauche');

        // Include modelo to access reencauches_maximos
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true });

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
            throw new Error(`El neumático debe estar EN_STOCK. Estado actual: ${neumatico.estado_actual}`);
        }

        // Validate max retreads (RF16) - using correct field names from schema
        if (neumatico.reencauches_realizados >= neumatico.modelo.reencauches_maximos) {
            throw new Error(`El neumático ha alcanzado el límite de reencauches (${neumatico.modelo.reencauches_maximos})`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA,
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
                estado_actual: EstadoNeumaticoEnum.EN_REENCAUCHE,
                ubicacion_almacen_id: null,
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: EstadoNeumaticoEnum.EN_REENCAUCHE,
                fecha_cambio: now,
                motivo: `Envío a reencauche`
            }
        });

        return nuevoEvento;
    }

    private async _handleReencaucheSalida(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para retorno de reencauche');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REENCAUCHE) {
            throw new Error(`El neumático no está en reencauche. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId,
            },
        });

        // Update tire - use correct field name from schema and remove non-existent cost field
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_actual_mm: profundidad_remanente || undefined,
                es_reencauchado: true,
                reencauches_realizados: { increment: 1 }, // Correct field name from schema
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: EstadoNeumaticoEnum.EN_STOCK,
                fecha_cambio: now,
                motivo: `Retorno de reencauche`
            }
        });

        return nuevoEvento;
    }

    private async _handleDesecho(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, motivo_desecho_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new Error('Faltan datos requeridos para desecho');

        const neumatico = await tx.neumatico.findUnique({ where: { id: neumatico_id } });
        if (!neumatico) throw new Error('Neumático no encontrado');

        // Can be discarded from almost any state except installed (should be dismounted first)
        if (neumatico.estado_actual === EstadoNeumaticoEnum.INSTALADO) {
            throw new Error('El neumático debe ser desmontado antes de desecharse');
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.DESECHO,
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
                estado_actual: EstadoNeumaticoEnum.DESECHADO,
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
                estado_nuevo: EstadoNeumaticoEnum.DESECHADO,
                fecha_cambio: now,
                motivo: `Baja definitiva`
            }
        });

        return nuevoEvento;
    }
}
