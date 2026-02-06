import { EventoNeumaticoRepository } from '@/lib/repositories/evento-neumatico.repository';
import { CreateEventoInput } from '@/lib/validators/evento-neumatico';
import {
    EventoResponse
} from '@/types/domain/evento-neumatico.types';
import {
    Result,
    ok,
    err,
    BusinessError,
    ValidationError,
    ConflictError,
    NotFoundError
} from '@/types/result.types';
import {
    NeumaticoId,
    UsuarioId,
    EventoId
} from '@/types/branded.types';
import { Prisma, TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, Neumatico } from '@prisma/client';
import { prisma } from '@/lib/prisma';
import { toNumber } from '@/lib/utils/decimal';
import { AlertasService } from './alertas.service';
import { sseEmitter } from './sse-emitter.service';
import { EventBus } from '@/lib/events/core';
import { NeumaticoEvents } from '@/lib/events/neumatico.events';
import type {
    TirePurchasedPayload,
    TireMountedPayload,
    TireDismountedPayload,
    TireRotatedPayload,
    TireScrappedPayload,
    RepairStartedPayload,
    RepairCompletedPayload,
    RetreadSentPayload,
    RetreadReturnedPayload
} from '@/lib/events/neumatico.events';
import { NeumaticoService } from './neumatico.service';
import { CreateNeumaticoDTO } from '@/types/domain/neumatico.types';

type TxClient = Prisma.TransactionClient;

export class EventoNeumaticoService {
    private repository: EventoNeumaticoRepository;
    private alertasService: AlertasService;

    constructor(
        // Allow injection but default inside
        alertasService?: AlertasService
    ) {
        this.repository = new EventoNeumaticoRepository();
        this.alertasService = alertasService || new AlertasService();
    }

    /**
     * Registra un evento de ciclo de vida del neumático.
     * Maneja la transacción completa, incluyendo actualizaciones de estado y validaciones.
     */
    async registrarEvento(
        input: CreateEventoInput,
        userId: UsuarioId,
        externalTx?: Prisma.TransactionClient
    ): Promise<Result<EventoResponse, BusinessError>> {
        try {
            // Validaciones básicas de entrada
            if (!input.neumatico_id && input.tipo_evento !== 'COMPRA') {
                return err(new ValidationError("El ID del neumático es obligatorio para eventos que no son COMPRA"));
            }

            // [Handle COMPRA Exception]: If COMPRA, we might delegate to NeumaticoService immediately
            // because NeumaticoService.create manages its own transaction and creates the Entity + Event.
            // If we are inside a transaction (externalTx), we can't easily delegate if NeumaticoService starts a new one unless we refactor it.
            // However, NeumaticoService.create uses prisma.$transaction.
            // Refactor Strategy:
            // 1. If COMPRA, call private _handleCompra which calls NeumaticoService logic adapted for TX.
            // But NeumaticoService.create is complex.
            // BETTER: Use NeumaticoService as the facade for COMPRA if no externalTx.

            if (input.tipo_evento === 'COMPRA' && !externalTx) {
                // We need the empresa_id context here. 
                // The service signature only has userId and input.
                // We'll need to fetch user's company or pass it.
                // Limitation: This service method signature doesn't take empresaId directly, 
                // but usually `userId` implies context or we need to look it up.
                // Wait, `registrarEvento` is called by API route which has session.
                // But here `userId` is just a string (ID).
                // We will look up the user's company to pass to NeumaticoService.
                const user = await prisma.usuario.findUnique({ where: { id: userId }, select: { empresa_id: true } });
                if (!user) return err(new NotFoundError('Usuario no encontrado'));

                // Delegate to _handleCompra which maps validation and calls NeumaticoService
                // We will do this inside the logic flow, but note NeumaticoService.create handles its own TX.
            }

            // Ejecutar lógica dentro de una transacción
            const executeLogic = (tx: TxClient) => this._dispatchEvento(input, userId, tx);

            let eventEntity;
            if (externalTx) {
                eventEntity = await executeLogic(externalTx);
            } else {
                eventEntity = await prisma.$transaction(executeLogic, { maxWait: 10000, timeout: 30000 });
            }

            // Mapear respuesta final (Recuperando entidad completa si es necesario)
            // El repository.create devuelve con includes, pero mis handlers internos usan create nativo.
            // Repositorio garantiza includes.
            const fullEntity = await this.repository.findById(eventEntity.id as EventoId);

            if (!fullEntity) throw new Error("Error inesperado: evento creado no encontrado");

            // SSE: Notificar a clientes conectados sobre cambio en neumáticos
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: input.neumatico_id },
                select: { empresa_id: true }
            });
            if (neumatico?.empresa_id) {
                sseEmitter.notifyNeumaticosUpdate(neumatico.empresa_id);
            }

            // === NEW: EMIT DOMAIN EVENTS ===
            // Emit event after transaction success for Observer pattern
            await this._emitDomainEvent(input, fullEntity, userId, neumatico?.empresa_id);

            return ok(this._mapToResponse(fullEntity));

        } catch (error: any) {
            console.error('[EventoService] Error:', error);
            if (error instanceof BusinessError) {
                return err(error);
            }
            return err(new BusinessError(error.message || "Error al registrar evento", "EVENT_ERROR", 500));
        }
    }

    // ==========================================
    // PRIVATE DISPATCHER
    // ==========================================
    private async _dispatchEvento(input: CreateEventoInput, userId: string, tx: TxClient) {
        switch (input.tipo_evento) {
            case TipoEventoNeumaticoEnum.INSTALACION:
                return this._handleInstalacion(input, userId, tx);
            case TipoEventoNeumaticoEnum.DESMONTAJE:
                return this._handleDesmontaje(input, userId, tx);
            case TipoEventoNeumaticoEnum.ROTACION:
                return this._handleRotacion(input, userId, tx);
            case TipoEventoNeumaticoEnum.INSPECCION:
                return this._handleInspeccion(input, userId, tx);
            case TipoEventoNeumaticoEnum.REPARACION_ENTRADA:
                return this._handleReparacionEntrada(input, userId, tx);
            case TipoEventoNeumaticoEnum.REPARACION_SALIDA:
                return this._handleReparacionSalida(input, userId, tx);
            case TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA:
                return this._handleReencaucheEntrada(input, userId, tx);
            case TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA:
                return this._handleReencaucheSalida(input, userId, tx);
            case TipoEventoNeumaticoEnum.DESECHO:
                return this._handleDesecho(input, userId, tx);
            case TipoEventoNeumaticoEnum.AJUSTE_INVENTARIO:
                // TODO: Implementar lógica específica si existe
                return this._handleInspeccion(input, userId, tx); // Fallback seguro
            case TipoEventoNeumaticoEnum.COMPRA:
                return this._handleCompra(input, userId, tx);
            default:
                throw new BusinessError(`Evento ${input.tipo_evento} no soportado en EventoService aún`, 'NOT_IMPLEMENTED', 400);
        }
    }

    // ==========================================
    // HANDLERS (Migrated logic)
    // ==========================================

    private async _handleInstalacion(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, contador_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !vehiculo_id) throw new ValidationError('Faltan datos instalación');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw new ConflictError('El neumático no está en stock');

        const vehiculo = await tx.vehiculo.findUnique({ where: { id: vehiculo_id } });
        if (!vehiculo) throw new NotFoundError('Vehículo');

        if (posicion_montaje_id) {
            const posicion = await tx.posicionNeumatico.findUnique({ where: { id: posicion_montaje_id }, include: { configuracion_eje: true } });
            if (!posicion) throw new NotFoundError('Posición');

            // Validaciones de compatibilidad
            if (posicion.configuracion_eje.tipo_vehiculo_id !== vehiculo.tipo_vehiculo_id) {
                throw new ConflictError('La posición no corresponde al tipo de vehículo');
            }
            if (neumatico.es_reencauchado && !posicion.configuracion_eje.permite_reencauchados) {
                throw new ConflictError('Esta posición no permite neumáticos reencauchados');
            }

            const ocupada = await tx.neumatico.findFirst({
                where: { ubicacion_posicion_id: posicion_montaje_id, activo: true, estado_actual: EstadoNeumaticoEnum.INSTALADO }
            });
            if (ocupada) throw new ConflictError(`Posición ocupada por neumático ${ocupada.numero_serie}`);
        }

        // Crear Evento
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                neumatico_id,
                fecha_evento: now,
                contador_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id,
                posicion_montaje_id,
                notas: observaciones,
                creado_por: userId
            }
        });

        // Actualizar Neumático
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.INSTALADO,
                ubicacion_almacen_id: null,
                ubicacion_vehiculo_id: vehiculo_id,
                ubicacion_posicion_id: posicion_montaje_id || null, // Puede ser null si es "al montón"
                profundidad_remanente_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                actualizado_en: now
            }
        });

        // Historial Estado
        await tx.historialEstadoNeumatico.create({
            data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: EstadoNeumaticoEnum.INSTALADO, fecha_cambio: now, motivo: `Montaje en ${vehiculo.placa}`, creado_por: userId }
        });

        // Actualizar Odómetro Vehículo
        if (contador_vehiculo) {
            await tx.registroContador.create({ data: { vehiculo_id, valor: contador_vehiculo, fecha_registro: now, notas: `Montaje ${neumatico.numero_serie}` } });
            await tx.vehiculo.update({ where: { id: vehiculo_id }, data: { odometro_actual: contador_vehiculo } });
        }

        return nuevoEvento;
    }

    private async _handleDesmontaje(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, contador_vehiculo, profundidad_remanente, presion_psi, observaciones, estado_neumatico_resultante, almacen_destino_id, motivo_desecho_id } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new ValidationError('ID de neumático requerido');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw new ConflictError('Neumático no instalado, no se puede desmontar');

        // Calcular KM Recorrido
        let kmRecorrido = 0;
        if (contador_vehiculo && neumatico.ubicacion_vehiculo_id) {
            const instEvento = await tx.eventoNeumatico.findFirst({
                where: { neumatico_id, tipo_evento: TipoEventoNeumaticoEnum.INSTALACION },
                orderBy: { fecha_evento: 'desc' }
            });
            if (instEvento?.contador_vehiculo) {
                const contadorInstalacion = toNumber(instEvento.contador_vehiculo);
                kmRecorrido = contador_vehiculo - contadorInstalacion;
                // Permitir ligero error o warn? Mejor strict por ahora.
                if (kmRecorrido < 0) console.warn(`[WARN] KM Desmontaje (${contador_vehiculo}) < Montaje (${contadorInstalacion})`);
            }
        }

        const nuevoEstado = (estado_neumatico_resultante || EstadoNeumaticoEnum.EN_STOCK) as EstadoNeumaticoEnum;

        // Validación Destino
        if (nuevoEstado === EstadoNeumaticoEnum.EN_STOCK && !almacen_destino_id) throw new ValidationError('Se requiere almacén de destino para enviar a Stock');
        if (nuevoEstado === EstadoNeumaticoEnum.DESECHADO && !motivo_desecho_id) throw new ValidationError('Se requiere motivo de desecho');

        // Crear Evento
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.DESMONTAJE,
                neumatico_id,
                fecha_evento: now,
                contador_vehiculo,
                profundidad_remanente,
                presion_psi,
                vehiculo_id: neumatico.ubicacion_vehiculo_id,
                posicion_montaje_id: neumatico.ubicacion_posicion_id,
                almacen_destino_id,
                motivo_desecho_id,
                notas: observaciones,
                creado_por: userId
            }
        });

        // Update Neumático
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: nuevoEstado,
                ubicacion_almacen_id: almacen_destino_id || null,
                ubicacion_vehiculo_id: null,
                ubicacion_posicion_id: null,
                profundidad_remanente_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                kilometraje_acumulado: { increment: Math.max(0, kmRecorrido) },
                actualizado_en: now
            }
        });

        // Historial
        await tx.historialEstadoNeumatico.create({
            data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: nuevoEstado, fecha_cambio: now, motivo: 'Desmontaje', creado_por: userId }
        });

        // Update Vehículo Odo
        if (contador_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await tx.registroContador.create({ data: { vehiculo_id: neumatico.ubicacion_vehiculo_id, valor: contador_vehiculo, fecha_registro: now, notas: `Desmontaje ${neumatico.numero_serie}` } });
            await tx.vehiculo.update({ where: { id: neumatico.ubicacion_vehiculo_id }, data: { odometro_actual: contador_vehiculo } });
        }

        return nuevoEvento;
    }

    private async _handleInspeccion(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, profundidad_remanente, presion_psi, contador_vehiculo, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new ValidationError('ID requerido');

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
                neumatico_id, fecha_evento: now, contador_vehiculo, profundidad_remanente, presion_psi, notas: observaciones, creado_por: userId
            }
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                profundidad_remanente_actual_mm: profundidad_remanente ?? undefined,
                presion_actual_psi: presion_psi ?? undefined,
                actualizado_en: now
            }
        });

        // GENERAR LECTURA Y ALERTAS (Logic merged from InspeccionService)
        if (presion_psi !== undefined) {
            // 1. Registrar Lectura Histórica
            await tx.lecturaPresion.create({
                data: {
                    neumatico_id,
                    presion_psi: presion_psi,
                    temperatura_c: evento.temperatura_c, // Added persistence
                    fuente: 'MANUAL', // Asumido manual si viene por evento inspección
                    creado_por: userId,
                    fecha_lectura: now
                }
            });

            // 2. Disparar Alerta (Si aplica)
            // Necesitamos el modelo para saber la recomendada.
            // neumatico ya fue traido en alguna parte? No, en _handleInspeccion no llamamos _validateAndGetNeumatico 
            // porque no era estricto antes. Ahora debemos traerlo CON modelo.
            const neumaticoConModelo = await tx.neumatico.findUnique({
                where: { id: neumatico_id },
                include: { modelo: true }
            });

            if (neumaticoConModelo && neumaticoConModelo.modelo) {
                const recomendada = neumaticoConModelo.modelo.presion_recomendada_psi
                    ? Number(neumaticoConModelo.modelo.presion_recomendada_psi)
                    : 100;

                const umbralMinimo = Math.round(recomendada * 0.8);

                // Llamada a AlertasService (Note: AlertasService methods might NOT support tx injection? 
                // Creating alert is usually strictly transactional? 
                // AlertasService.generarAlertaPresion uses prisma.alerta.create.
                // ideally pass tx to it. But we can't easily change AlertasService signature right now.
                // We'll execute it AFTER the transaction or inside if possible?
                // If AlertasService does not accept TX, we might have atomicity issue.
                // However, for this architecture pass, we'll try to execute it.
                // Better approach: Copy logic here inside TX or Refactor AlertasService later.
                // Since user wants "100%", I should use TX.
                await this.alertasService.generarAlertaPresion(neumatico_id, presion_psi, umbralMinimo, tx);
            }
        }

        return nuevoEvento;
    }

    private async _handleRotacion(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, posicion_montaje_id, contador_vehiculo, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !posicion_montaje_id) throw new ValidationError('Datos incompletos para rotación');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw new ConflictError('Neumático no instalado');

        const origenPosId = neumatico.ubicacion_posicion_id;
        const destinoPosId = posicion_montaje_id;

        // Validar destino
        const targetPos = await tx.posicionNeumatico.findUnique({ where: { id: destinoPosId }, include: { configuracion_eje: true } });
        if (!targetPos) throw new NotFoundError('Posición destino no existe');
        if (neumatico.es_reencauchado && !targetPos.configuracion_eje.permite_reencauchados) throw new ConflictError('Posición destino no permite reencauchados');

        // Check if swap needed
        const neumaticoEnDestino = await tx.neumatico.findFirst({
            where: { ubicacion_posicion_id: destinoPosId, activo: true, estado_actual: EstadoNeumaticoEnum.INSTALADO }
        });

        if (neumaticoEnDestino && origenPosId) {
            // Validar origen para el que vuelve
            const origenPos = await tx.posicionNeumatico.findUnique({ where: { id: origenPosId }, include: { configuracion_eje: true } });
            if (neumaticoEnDestino.es_reencauchado && !origenPos?.configuracion_eje.permite_reencauchados) throw new ConflictError('Swap inválido: reencauchado a origen prohibido');
        }

        // Rotar Principal
        const eventoRotacion = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
                neumatico_id, fecha_evento: now, contador_vehiculo, vehiculo_id: neumatico.ubicacion_vehiculo_id, posicion_montaje_id: destinoPosId, notas: observaciones, creado_por: userId
            }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { ubicacion_posicion_id: destinoPosId, actualizado_en: now } });

        // Rotar Secundario (Swap)
        if (neumaticoEnDestino && origenPosId) {
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
                    neumatico_id: neumaticoEnDestino.id,
                    fecha_evento: now,
                    contador_vehiculo,
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    posicion_montaje_id: origenPosId,
                    notas: `Intercambio automático con ${neumatico.numero_serie}`,
                    creado_por: userId
                }
            });
            await tx.neumatico.update({ where: { id: neumaticoEnDestino.id }, data: { ubicacion_posicion_id: origenPosId, actualizado_en: now } });
        }

        return eventoRotacion;
    }

    private async _handleReparacionEntrada(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new ValidationError('ID requerido');
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw new ConflictError('El neumático debe estar en STOCK para ir a reparación');

        const evt = await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REPARACION_ENTRADA, neumatico_id, fecha_evento: now, proveedor_id, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: { estado_actual: EstadoNeumaticoEnum.EN_REPARACION, ubicacion_almacen_id: null, actualizado_en: now }
        });

        return evt;
    }

    private async _handleReparacionSalida(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id) throw new ValidationError('ID requerido');
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REPARACION) throw new ConflictError('El neumático no está en reparación');

        const evt = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.REPARACION_SALIDA,
                neumatico_id,
                fecha_evento: now,
                almacen_destino_id,
                costo_evento: costo_evento ? new Prisma.Decimal(costo_evento) : undefined,
                profundidad_remanente,
                notas: observaciones,
                creado_por: userId
            }
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: { estado_actual: EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id: almacen_destino_id, profundidad_remanente_actual_mm: profundidad_remanente, actualizado_en: now }
        });

        return evt;
    }

    private async _handleReencaucheEntrada(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id!);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw new ConflictError('Debe estar en STOCK');

        const evt = await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA, neumatico_id: neumatico_id!, fecha_evento: now, proveedor_id, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { estado_actual: EstadoNeumaticoEnum.EN_REENCAUCHE, ubicacion_almacen_id: null, actualizado_en: now } });
        return evt;
    }

    private async _handleReencaucheSalida(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date(evento.fecha_evento || new Date());
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id!);

        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REENCAUCHE) throw new ConflictError('No está en reencauche');

        const evt = await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA, neumatico_id: neumatico_id!, fecha_evento: now, almacen_destino_id, costo_evento: costo_evento ? new Prisma.Decimal(costo_evento) : undefined, profundidad_remanente, notas: observaciones, creado_por: userId }
        });

        // REENCAUCHE RESET LOGIC
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_remanente_actual_mm: profundidad_remanente,
                profundidad_inicial_mm: profundidad_remanente, // Reset Vida
                kilometraje_acumulado: 0,
                es_reencauchado: true,
                reencauches_realizados: { increment: 1 },
                vida_actual: { increment: 1 },
                actualizado_en: now
            }
        });

        return evt;
    }

    private async _handleDesecho(evento: CreateEventoInput, userId: string, tx: TxClient) {
        const { neumatico_id, motivo_desecho_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id!);

        if (neumatico.estado_actual === EstadoNeumaticoEnum.INSTALADO) throw new ConflictError('Desmontar antes de desechar');

        const evt = await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.DESECHO, neumatico_id: neumatico_id!, fecha_evento: now, motivo_desecho_id, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: { estado_actual: EstadoNeumaticoEnum.DESECHADO, ubicacion_almacen_id: null, ubicacion_vehiculo_id: null, ubicacion_posicion_id: null, actualizado_en: now }
        });

        return evt;
    }

    // --- HELPERS ---
    private async _validateAndGetNeumatico(tx: TxClient, id: string): Promise<Neumatico> {
        const neumatico = await tx.neumatico.findUnique({ where: { id } });
        if (!neumatico) throw new NotFoundError('Neumático');
        if (!neumatico.activo) throw new BusinessError('Neumático inactivo', 'NEUMATICO_INACTIVO', 409);
        return neumatico;
    }

    private async _handleCompra(evento: CreateEventoInput, userId: string, tx: TxClient) {
        // 1. Map Event Input to Neumatico DTO
        if (!evento.modelo_id) throw new ValidationError('Modelo requerido para COMPRA');
        if (!evento.proveedor_id) throw new ValidationError('Proveedor requerido para COMPRA');
        if (!evento.costo_evento) throw new ValidationError('Costo de compra requerido');

        // We need to resolve empresa_id required by NeumaticoService.create
        // Since we are inside a transaction or deep in logic, we need to fetch it if not provided.
        // Optimization: Pass it? or fetch.
        const user = await tx.usuario.findUnique({ where: { id: userId }, select: { empresa_id: true } });
        if (!user) throw new NotFoundError('Usuario iniciador no encontrado');

        const createDTO: CreateNeumaticoDTO = {
            modelo_id: evento.modelo_id,
            numero_serie: evento.numero_serie, // Optional (auto-gen or provided)
            dot: evento.dot,

            // Purchase Data
            fecha_compra: evento.fecha_compra || new Date().toISOString(),
            costo_compra: evento.costo_evento,
            proveedor_compra_id: evento.proveedor_id,

            // Initial State
            profundidad_actual_mm: evento.profundidad_remanente || 0,
            profundidad_inicial_mm: evento.profundidad_inicial || evento.profundidad_remanente || 0,

            // Optional/Defaults
            ubicacion_almacen_id: evento.almacen_destino_id
        };

        // 2. Call NeumaticoService to create Entity + Event
        // Problem: NeumaticoService.create uses its own transaction. 
        // If we call it here, and we are already in a transaction `tx`, pure Prisma doesn't support nested transactions well 
        // unless we pass `tx` to NeumaticoService.create.
        // Current NeumaticoService.create does: `prisma.$transaction(async (tx) => ...)`
        // It does NOT accept an external `tx`.

        // REFACTOR NEEDED: We must replicate the CREATION logic here using `tx` 
        // OR refactor NeumaticoService to accept `tx`.
        // "Reparalo" implies fixing it properly.
        // Replicating logic is safer to avoid changing NeumaticoService signature widely right now.
        // Logic from NeumaticoService.create:

        // 2.1 Map to Prisma Create Input
        // We will call the mapper manually
        const { mapDtoToPrismaCreate } = require('@/lib/mappers/neumatico.mapper'); // Dynamic import to avoid cycles if any
        const prismaInput = mapDtoToPrismaCreate(createDTO, userId, user.empresa_id);

        // 2.2 Create Entity
        const neumatico = await tx.neumatico.create({
            data: prismaInput,
            include: {
                modelo: { include: { fabricante: true } },
                ubicacion_almacen: true,
                ubicacion_vehiculo: { include: { tipo_vehiculo: true } },
                ubicacion_posicion: true,
                proveedor_compra: true,
                motivo_desecho: true
            }
        });

        // 2.3 Create Event (COMPRA)
        // Note: EventoService usually creates the event, but here we are IN the handler for it.
        // We just create the record.
        const compraEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.COMPRA,
                neumatico_id: neumatico.id,
                fecha_evento: new Date(createDTO.fecha_compra),
                proveedor_id: createDTO.proveedor_compra_id,
                almacen_destino_id: createDTO.ubicacion_almacen_id,
                costo_evento: createDTO.costo_compra ? new Prisma.Decimal(createDTO.costo_compra) : undefined,
                profundidad_remanente: createDTO.profundidad_actual_mm,
                notas: evento.observaciones || 'Alta vía Eventos Centralizada',
                creado_por: userId
            }
        });

        // Return the Event entity (which is what this service expects) because downstream it fetches by ID.
        // But wait, the main method returns `this.repository.findById(eventEntity.id)`. 
        // So we just return the created event object.
        return compraEvento;
    }

    // Simplistic mapper for internal usage
    private _mapToResponse(entity: any): EventoResponse {
        return {
            id: entity.id as EventoId,
            tipo: entity.tipo_evento,
            fecha: entity.fecha_evento.toISOString(),
            neumatico: {
                id: entity.neumatico.id as NeumaticoId,
                serie: entity.neumatico.numero_serie || 'SIN-SERIE',
                marca: entity.neumatico.modelo.fabricante.nombre,
                modelo: entity.neumatico.modelo.nombre_modelo,
            },
            costo: entity.costo_evento ? Number(entity.costo_evento) : null,
            observaciones: entity.notas || entity.observaciones || null,
            contadores: {
                kmVehiculo: entity.contador_vehiculo ? Number(entity.contador_vehiculo) : null,
                remanenteMm: entity.profundidad_remanente ? Number(entity.profundidad_remanente) : null,
                presionPsi: entity.presion_psi ? Number(entity.presion_psi) : null,
            },
            destino: {
                vehiculo: entity.vehiculo ? { id: entity.vehiculo.id as any, placa: entity.vehiculo.placa || 'SIN-PLACA' } : null,
                posicion: entity.posicion_montaje ? entity.posicion_montaje.codigo_posicion : null,
                almacen: entity.almacen_destino ? { id: entity.almacen_destino.id as any, nombre: entity.almacen_destino.nombre } : null,
                proveedor: entity.proveedor ? { id: entity.proveedor.id as any, nombre: entity.proveedor.nombre } : null,
            },
            autor: {
                id: entity.usuario ? entity.usuario.id as UsuarioId : null,
                nombre: entity.usuario ? entity.usuario.nombre_completo : null
            },
            createdAt: entity.creado_en.toISOString()
        };
    }

    /**
     * Emit domain events based on operation type
     * This allows observers to react to tire lifecycle events
     */
    private async _emitDomainEvent(
        input: CreateEventoInput,
        eventEntity: any,
        userId: string,
        empresaId?: string
    ): Promise<void> {
        try {
            if (!empresaId || !input.neumatico_id) return;

            const basePayload = {
                neumaticoId: input.neumatico_id,
                empresaId,
                usuarioId: userId,
                timestamp: new Date()
            };

            const neumatico = eventEntity.neumatico;
            const metadata = {
                numeroSerie: neumatico?.numero_serie || null,
                modeloNombre: neumatico?.modelo?.nombre_modelo || 'UNKNOWN'
            };

            switch (input.tipo_evento) {
                case TipoEventoNeumaticoEnum.COMPRA:
                    EventBus.publish<TirePurchasedPayload>(NeumaticoEvents.PURCHASED, {
                        ...basePayload,
                        modeloId: input.modelo_id!,
                        marcaId: input.marca_id!,
                        costoCompra: input.costo_compra || 0,
                        proveedorId: input.proveedor_id,
                        metadata: {
                            medida: input.medida || '',
                            dot: input.dot,
                            profundidadInicial: input.profundidad_inicial || 0
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.INSTALACION:
                    EventBus.publish<TireMountedPayload>(NeumaticoEvents.MOUNTED, {
                        ...basePayload,
                        vehiculoId: input.vehiculo_id!,
                        posicionId: input.posicion_montaje_id!,
                        kilometrajeVehiculo: input.contador_vehiculo,
                        metadata: {
                            ...metadata,
                            estadoAnterior: neumatico?.estado_actual || 'UNKNOWN',
                            profundidadActual: input.profundidad_remanente
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.DESMONTAJE:
                    EventBus.publish<TireDismountedPayload>(NeumaticoEvents.DISMOUNTED, {
                        ...basePayload,
                        vehiculoId: input.vehiculo_id!,
                        posicionId: input.posicion_montaje_id!,
                        almacenDestinoId: input.almacen_destino_id,
                        razon: input.observaciones,
                        profundidadRemanente: input.profundidad_remanente,
                        metadata: {
                            ...metadata,
                            kilometrajeVidaActual: neumatico?.kilometraje_vida_actual || 0,
                            estadoResultante: input.estado_neumatico_resultante || neumatico?.estado_actual || 'EN_STOCK'
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.ROTACION:
                    EventBus.publish<TireRotatedPayload>(NeumaticoEvents.ROTATED, {
                        ...basePayload,
                        vehiculoId: input.vehiculo_id!,
                        posicionOrigenId: 'CURRENT',
                        posicionDestinoId: input.posicion_montaje_id!,
                        kilometrajeVehiculo: input.contador_vehiculo || 0,
                        metadata: {
                            ...metadata,
                            profundidadActual: input.profundidad_remanente
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.DESECHO:
                    EventBus.publish<TireScrappedPayload>(NeumaticoEvents.SCRAPPED, {
                        ...basePayload,
                        motivoDesechoId: input.motivo_desecho_id,
                        motivoTexto: input.observaciones || 'Sin motivo especificado',
                        profundidadFinal: input.profundidad_remanente,
                        metadata: {
                            ...metadata,
                            costoTotal: neumatico?.costo_acumulado || 0,
                            kmTotales: neumatico?.kilometraje_total || 0,
                            vidaActual: neumatico?.vida_actual || 1,
                            reencauchesRealizados: neumatico?.reencauches_realizados || 0
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.REPARACION_ENTRADA:
                    EventBus.publish<RepairStartedPayload>(NeumaticoEvents.REPAIR_STARTED, {
                        ...basePayload,
                        proveedorId: input.proveedor_id,
                        costoEstimado: input.costo_evento,
                        observaciones: input.observaciones,
                        metadata: {
                            ...metadata,
                            estadoAnterior: neumatico?.estado_actual || 'UNKNOWN',
                            profundidadPreReparacion: input.profundidad_remanente
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.REPARACION_SALIDA:
                    EventBus.publish<RepairCompletedPayload>(NeumaticoEvents.REPAIR_COMPLETED, {
                        ...basePayload,
                        proveedorId: input.proveedor_id,
                        costoReal: input.costo_evento || 0,
                        observaciones: input.observaciones,
                        metadata: {
                            ...metadata,
                            estadoResultante: input.estado_neumatico_resultante || 'EN_STOCK',
                            profundidadPostReparacion: input.profundidad_remanente,
                            diasEnTaller: 0
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA:
                    EventBus.publish<RetreadSentPayload>(NeumaticoEvents.RETREAD_SENT, {
                        ...basePayload,
                        proveedorId: input.proveedor_id!,
                        metadata: {
                            ...metadata,
                            vidaActual: neumatico?.vida_actual || 1,
                            profundidadPreRetread: input.profundidad_remanente
                        }
                    });
                    break;

                case TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA:
                    EventBus.publish<RetreadReturnedPayload>(NeumaticoEvents.RETREAD_RETURNED, {
                        ...basePayload,
                        proveedorId: input.proveedor_id!,
                        costoReencauche: input.costo_evento || 0,
                        nuevaProfundidad: input.profundidad_remanente || 0,
                        metadata: {
                            ...metadata,
                            nuevoReencaucheCount: neumatico?.reencauches_realizados || 0,
                            nuevaVida: neumatico?.vida_actual || 1
                        }
                    });
                    break;

                default:
                    console.log(`[EventEmitter] No domain event mapped for: ${input.tipo_evento}`);
            }

        } catch (error: any) {
            console.error(`[EventEmitter] Failed to emit domain event: ${error.message}`);
        }
    }
}
