import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, INeumatico, NeumaticoFilters } from '@/types/domain/neumatico.types';
import { prisma } from '@/lib/prisma';
import { EventoNeumaticoCreate } from '@/lib/validators/evento-neumatico';
import { TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, Prisma } from '@prisma/client';
import { BusinessError } from '@/lib/errors/business.error';

// Type for Prisma transaction client
type TxClient = Prisma.TransactionClient;

// Type for Neumatico with modelo relation included
type NeumaticoConModelo = Prisma.NeumaticoGetPayload<{
    include: { modelo: true }
}>;

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
        const existing = await this.repository.findBySerie(data.numero_serie);
        if (existing) {
            throw BusinessError.conflict(`El neumático con serie ${data.numero_serie} ya existe.`);
        }
        return await this.repository.create(data);
    }

    async update(id: string, data: UpdateNeumaticoDTO): Promise<INeumatico> {
        const existing = await this.repository.findById(id);
        if (!existing) throw BusinessError.notFound('Neumático', id);
        return await this.repository.update(id, data);
    }

    async delete(id: string): Promise<INeumatico> {
        return await this.repository.delete(id);
    }

    /**
     * MÉTODO CENTRALIZADO TRANSACCIONAL
     * Orquesta todos los cambios de estado y registro de eventos.
     */
    async registrarEvento(evento: EventoNeumaticoCreate, userId: string): Promise<any> {
        const { tipo_evento } = evento;

        return await prisma.$transaction(async (tx) => {
            let result;

            switch (tipo_evento) {
                case TipoEventoNeumaticoEnum.COMPRA:
                    result = await this._handleCompra(evento, userId, tx);
                    break;
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
                default:
                    throw new Error(`Evento ${tipo_evento} no soportado aún.`);
            }

            return result;
        });
    }

    // --- MANEJADORES DE EVENTOS PRIVADOS ---

    private async _validateAndGetNeumatico(tx: TxClient, id: string, includes: any = {}) {
        const neumatico = await tx.neumatico.findUnique({
            where: { id },
            include: includes
        });

        if (!neumatico) throw BusinessError.notFound('Neumático', id);
        if (!neumatico.activo) throw BusinessError.badRequest('El neumático no está activo');

        return neumatico;
    }

    /**
     * Handle COMPRA event - Creates new tire and registers purchase event
     * Per RF01: Tire creation must go through event system for full lifecycle tracking
     */
    private async _handleCompra(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const {
            numero_serie,
            modelo_id,
            dot,
            profundidad_inicial,
            fecha_compra,
            costo_compra,
            almacen_destino_id,
            proveedor_id,
            observaciones
        } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        // 1. Validate required fields for purchase
        if (!numero_serie || !modelo_id || !dot) {
            throw BusinessError.badRequest('Faltan datos requeridos: numero_serie, modelo_id y dot son obligatorios');
        }

        // 2. Check if tire already exists
        const existing = await tx.neumatico.findUnique({
            where: { numero_serie }
        });
        if (existing) {
            throw BusinessError.conflict(`El neumático con serie ${numero_serie} ya existe`);
        }

        // 3. Create tire
        const nuevoNeumatico = await tx.neumatico.create({
            data: {
                numero_serie,
                modelo_id,
                dot,
                profundidad_inicial_mm: profundidad_inicial || 0,
                profundidad_actual_mm: profundidad_inicial || 0,
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen_destino_id || null,
                fecha_compra: fecha_compra ? new Date(fecha_compra) : now,
                costo_compra: costo_compra ? new Prisma.Decimal(costo_compra) : undefined,
                activo: true,
                creado_en: now,
            }
        });

        // 4. Create COMPRA event for full lifecycle tracking
        const eventoCompra = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.COMPRA,
                neumatico_id: nuevoNeumatico.id,
                fecha_evento: now,
                almacen_destino_id,
                proveedor_id,
                costo_evento: costo_compra ? new Prisma.Decimal(costo_compra) : undefined,
                profundidad_remanente: profundidad_inicial,
                notas: observaciones,
                creado_por: userId,
            }
        });

        // 5. Create initial history record
        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: nuevoNeumatico.id,
                estado_anterior: null, // First state
                estado_nuevo: EstadoNeumaticoEnum.EN_STOCK,
                fecha_cambio: now,
                motivo: 'Compra inicial'
            }
        });

        return { evento: eventoCompra, neumatico: nuevoNeumatico };
    }

    private async _handleInstalacion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !vehiculo_id) throw BusinessError.badRequest('Faltan datos requeridos para instalación');

        // 1. Validate Tire
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true });

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
            throw BusinessError.conflict(`El neumático no está en stock. Estado actual: ${neumatico.estado_actual}`);
        }

        // 2. Validate Vehicle
        const vehiculo = await tx.vehiculo.findUnique({ where: { id: vehiculo_id } });
        if (!vehiculo) throw BusinessError.notFound('Vehículo', vehiculo_id);

        // 3. Validate Position (if provided)
        if (posicion_montaje_id) {
            // Validation: Position must belong to the vehicle type
            const posicion = await tx.posicionNeumatico.findUnique({
                where: { id: posicion_montaje_id },
                include: { configuracion_eje: true }
            });

            if (!posicion) {
                throw BusinessError.notFound('Posición', posicion_montaje_id);
            }

            // Validate position belongs to vehicle type
            if (posicion.configuracion_eje.tipo_vehiculo_id !== vehiculo.tipo_vehiculo_id) {
                throw BusinessError.badRequest('La posición no corresponde al tipo de vehículo');
            }

            // Validate retreaded tire restrictions (RF16)
            if (neumatico.es_reencauchado && !posicion.configuracion_eje.permite_reencauchados) {
                throw BusinessError.badRequest('Esta posición no permite neumáticos reencauchados (RF16)');
            }

            // Check if position is occupied
            const posicionOcupada = await tx.neumatico.findFirst({
                where: {
                    ubicacion_posicion_id: posicion_montaje_id,
                    activo: true,
                    estado_actual: EstadoNeumaticoEnum.INSTALADO,
                }
            });

            if (posicionOcupada) {
                throw BusinessError.conflict(`La posición ya está ocupada por el neumático ${posicionOcupada.numero_serie}`);
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

        // 6. Create State History
        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: EstadoNeumaticoEnum.INSTALADO,
                fecha_cambio: now,
                motivo: `Instalación en vehículo ${vehiculo.placa}`
            }
        });

        // 7. Log Measurement
        if (profundidad_remanente || presion_psi) {
            await tx.medicionNeumatico.create({
                data: {
                    neumatico_id,
                    profundidad_mm: profundidad_remanente,
                    presion_psi,
                    kilometraje_registro: kilometraje_vehiculo,
                    fecha_medicion: now
                }
            });
        }

        // 8. Update Vehicle Odometer
        if (kilometraje_vehiculo) {
            await this._actualizarOdometro(tx, vehiculo_id, kilometraje_vehiculo, userId, now, `Instalación ${neumatico.numero_serie}`);
        }

        return nuevoEvento;
    }

    private async _handleDesmontaje(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones, estado_neumatico_resultante, almacen_destino_id, motivo_desecho_id } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        // 1. Validate Tire
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) {
            throw BusinessError.badRequest(`El neumático no está instalado. Estado actual: ${neumatico.estado_actual}`);
        }

        // 2. Calculate accumulated mileage
        if (neumatico.fecha_instalacion && kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            const eventos = await tx.eventoNeumatico.findMany({
                where: {
                    neumatico_id: neumatico_id,
                    tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                },
                orderBy: { fecha_evento: 'desc' }
            });

            const lastInstalacion = eventos[0]; // Latest first
            if (lastInstalacion?.kilometraje_vehiculo) {
                let kmRecorrido = kilometraje_vehiculo - lastInstalacion.kilometraje_vehiculo;
                // 🚨 CRITICAL FIX: Throw error instead of silently setting to 0
                if (kmRecorrido < 0) {
                    throw BusinessError.badRequest(
                        `Kilometraje inválido: El kilometraje actual (${kilometraje_vehiculo}) es menor que ` +
                        `el de la última instalación (${lastInstalacion.kilometraje_vehiculo}). ` +
                        `Verifique el odómetro del vehículo.`
                    );
                }
                await tx.neumatico.update({
                    where: { id: neumatico_id },
                    data: { kilometraje_acumulado: { increment: kmRecorrido } }
                });
            }
        }

        // 3. Determine Destination State and Event Type
        let nuevoEstado = estado_neumatico_resultante || EstadoNeumaticoEnum.EN_STOCK;

        // Validation based on destination
        if (nuevoEstado === EstadoNeumaticoEnum.EN_STOCK && !almacen_destino_id) {
            throw BusinessError.badRequest('Debe especificar un almacén destino para devolver a stock');
        }
        if (nuevoEstado === EstadoNeumaticoEnum.DESECHADO && !motivo_desecho_id) {
            throw BusinessError.badRequest('Debe especificar un motivo para el desecho');
        }

        // 4. Create Event
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.DESMONTAJE,
                neumatico_id,
                fecha_evento: now,
                kilometraje_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id: neumatico.ubicacion_vehiculo_id,
                posicion_montaje_id: neumatico.ubicacion_posicion_id,
                almacen_destino_id,
                motivo_desecho_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        // 5. Update Tire State
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: nuevoEstado,
                ubicacion_almacen_id: almacen_destino_id || null,
                ubicacion_vehiculo_id: null,
                ubicacion_posicion_id: null,
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                fecha_desecho: nuevoEstado === EstadoNeumaticoEnum.DESECHADO ? now : null,
                actualizado_en: now,
            },
        });

        // 6. State History
        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: nuevoEstado,
                fecha_cambio: now,
                motivo: nuevoEstado === EstadoNeumaticoEnum.DESECHADO ? 'Desecho' : 'Desmontaje'
            }
        });

        // 7. Update Vehicle Odometer
        if (kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await this._actualizarOdometro(tx, neumatico.ubicacion_vehiculo_id, kilometraje_vehiculo, userId, now, `Desmontaje ${neumatico.numero_serie}`);
        }

        return nuevoEvento;
    }

    private async _handleInspeccion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, profundidad_remanente, presion_psi, kilometraje_vehiculo, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
                neumatico_id,
                fecha_evento: now,
                kilometraje_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id: neumatico.ubicacion_vehiculo_id,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                actualizado_en: now,
            },
        });

        if (profundidad_remanente || presion_psi) {
            await tx.medicionNeumatico.create({
                data: {
                    neumatico_id,
                    profundidad_mm: profundidad_remanente,
                    presion_psi,
                    kilometraje_registro: kilometraje_vehiculo,
                    fecha_medicion: now
                }
            });
        }

        if (kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await this._actualizarOdometro(tx, neumatico.ubicacion_vehiculo_id, kilometraje_vehiculo, userId, now, `Inspección ${neumatico.numero_serie}`);
        }

        // TODO: Implementar sistema de alertas basado en especificaciones_desgaste
        // 
        // La tabla ModeloNeumatico NO tiene profundidad_minima_recomendada_mm.
        // Este campo está en la tabla especificaciones_desgaste, que relaciona:
        // - modelo_id (del neumático)
        // - tipo_vehiculo_id (del vehículo donde está instalado)
        // 
        // Implementación sugerida:
        // const specs = await tx.especificacionesDesgaste.findFirst({
        //     where: {
        //         modelo_id: neumatico.modelo_id,
        //         tipo_vehiculo_id: neumatico.ubicacion_vehiculo?.tipo_vehiculo_id,
        //         activo: true
        //     }
        // });
        // 
        // if (specs && profundidad_remanente <= Number(specs.profundidad_minima_recomendada_mm)) {
        //     await tx.alerta.create({ /* ... */ });
        // }

        return nuevoEvento;
    }

    private async _handleRotacion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !posicion_montaje_id) {
            throw BusinessError.badRequest('Faltan datos requeridos para rotación');
        }

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true });

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw BusinessError.badRequest('El neumático debe estar INSTALADO para rotarse');
        if (!neumatico.ubicacion_vehiculo_id) throw BusinessError.badRequest('El neumático no está asignado a ningún vehículo');

        const currentPosId = neumatico.ubicacion_posicion_id;
        const targetPosId = posicion_montaje_id;

        if (currentPosId === targetPosId) throw BusinessError.badRequest('La posición de destino es la misma que la actual');

        // 2. Validate Target Position and fetch position details for validation
        const targetPosition = await tx.posicionNeumatico.findUnique({
            where: { id: targetPosId },
            include: { configuracion_eje: true }
        });

        if (!targetPosition) throw BusinessError.notFound('Posición de destino', targetPosId);

        // Validate Tire A can go to target position (reencauche check)
        if (neumatico.es_reencauchado && !targetPosition.configuracion_eje.permite_reencauchados) {
            throw BusinessError.badRequest('El neumático reencauchado no puede instalarse en esta posición');
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

            if (!originPosition) throw BusinessError.notFound('Posición de origen', currentPosId);

            // Validate that Tire B can go to origin position (Tire A's old position)
            if (neumaticoEnDestino.es_reencauchado && !originPosition.configuracion_eje.permite_reencauchados) {
                throw BusinessError.badRequest(
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

        // 6. Record Measurements
        if (profundidad_remanente || presion_psi) {
            await tx.medicionNeumatico.create({
                data: {
                    neumatico_id,
                    profundidad_mm: profundidad_remanente,
                    presion_psi,
                    kilometraje_registro: kilometraje_vehiculo,
                    fecha_medicion: now
                }
            });
        }

        // 7. Update Odometer
        if (kilometraje_vehiculo) {
            await this._actualizarOdometro(tx, neumatico.ubicacion_vehiculo_id, kilometraje_vehiculo, userId, now, `Rotación ${neumatico.numero_serie}`);
        }

        return eventoRotacion;
    }

    private async _handleReparacionEntrada(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
            throw BusinessError.badRequest(`El neumático debe estar EN_STOCK. Estado actual: ${neumatico.estado_actual}`);
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
                ubicacion_almacen_id: null,
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

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REPARACION) {
            throw BusinessError.badRequest(`El neumático no está en reparación. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REPARACION_SALIDA,
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento: costo_evento ? new Prisma.Decimal(costo_evento) : undefined,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId,
            },
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
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

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        // Include modelo to access reencauches_maximos
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true }) as unknown as NeumaticoConModelo;

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
            throw BusinessError.badRequest(`El neumático debe estar EN_STOCK. Estado actual: ${neumatico.estado_actual}`);
        }

        // Validate max retreads (RF16) - TypeScript now knows modelo exists and has reencauches_maximos
        if (!neumatico.modelo) {
            throw BusinessError.badRequest('No se pudo obtener información del modelo del neumático');
        }

        if (neumatico.reencauches_realizados >= neumatico.modelo.reencauches_maximos) {
            throw BusinessError.conflict(`El neumático ha alcanzado el límite de reencauches (${neumatico.modelo.reencauches_maximos})`);
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

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REENCAUCHE) {
            throw BusinessError.badRequest(`El neumático no está en reencauche. Estado actual: ${neumatico.estado_actual}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento: costo_evento ? new Prisma.Decimal(costo_evento) : undefined,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId,
            },
        });

        // Update tire - CRITICAL: Reset lifecycle for new tread life (RF requirements)
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_actual_mm: profundidad_remanente || undefined,
                profundidad_inicial_mm: profundidad_remanente || undefined, // New "life" starts with this depth
                kilometraje_acumulado: 0, // CRITICAL: Reset to measure retreaded tire life for CPK
                es_reencauchado: true,
                reencauches_realizados: { increment: 1 },
                actualizado_en: now,
            },
        });

        await tx.historialEstadoNeumatico.create({
            data: {
                neumatico_id: neumatico.id,
                estado_anterior: neumatico.estado_actual,
                estado_nuevo: EstadoNeumaticoEnum.EN_STOCK,
                fecha_cambio: now,
                motivo: `Retorno de reencauche (Nueva vida)`
            }
        });

        return nuevoEvento;
    }

    private async _handleDesecho(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, motivo_desecho_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw BusinessError.badRequest('Falta neumatico_id');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual === EstadoNeumaticoEnum.INSTALADO) {
            throw BusinessError.badRequest('El neumático está instalado. Debe desmontarlo primero.');
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
                motivo: `Desecho definitivo`
            }
        });

        return nuevoEvento;
    }

    // Helper method to avoid repeating odometer logic
    private async _actualizarOdometro(tx: TxClient, vehiculo_id: string, kilometraje: number, userId: string, fecha: Date, notas: string) {
        await tx.registroOdometro.create({
            data: {
                vehiculo_id,
                kilometraje,
                fecha_registro: fecha,
                registrado_por: userId,
                notas
            }
        });

        await tx.vehiculo.update({
            where: { id: vehiculo_id },
            data: { kilometraje_actual: kilometraje }
        });
    }
}
