import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, INeumatico, NeumaticoFilters } from '@/types/domain/neumatico.types';
import { prisma } from '@/lib/prisma';
import { EventoNeumaticoCreate } from '@/lib/validators/evento-neumatico';
import { TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, Prisma } from '@prisma/client';
import { BusinessError } from '@/lib/errors/business.error';

// Tipado seguro para la transacción
type TxClient = Prisma.TransactionClient;

// Definición extendida para typescript dentro del servicio
interface EventoCompra extends EventoNeumaticoCreate {
    numero_serie?: string;
    modelo_id?: string;
    dot?: string;
    profundidad_inicial?: number;
    costo_compra?: number;
}

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

    // --- MÉTODO PRINCIPAL DE TRANSACCIÓN ---
    async registrarEvento(evento: EventoNeumaticoCreate, userId: string): Promise<any> {
        const { tipo_evento } = evento;

        return await prisma.$transaction(async (tx) => {
            let result;

            switch (tipo_evento) {
                // ✅ FIX CRÍTICO 1: El evento COMPRA ahora es ciudadano de primera clase
                case TipoEventoNeumaticoEnum.COMPRA:
                    result = await this._handleCompra(evento as EventoCompra, userId, tx);
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

    // --- MANEJADORES PRIVADOS ---

    private async _validateAndGetNeumatico(tx: TxClient, id: string, includes: any = {}) {
        const neumatico = await tx.neumatico.findUnique({ where: { id }, include: includes });
        if (!neumatico) throw BusinessError.notFound('Neumático', id);
        if (!neumatico.activo) throw BusinessError.badRequest('El neumático no está activo');
        return neumatico;
    }

    // ✅ LÓGICA DE COMPRA (NUEVA)
    private async _handleCompra(evento: EventoCompra, userId: string, tx: TxClient) {
        const { numero_serie, modelo_id, dot, profundidad_inicial, costo_compra, fecha_evento, proveedor_id, almacen_destino_id, notas } = evento;
        const now = new Date(fecha_evento || new Date());

        if (!numero_serie || !modelo_id || !dot || !profundidad_inicial || !almacen_destino_id) {
            throw BusinessError.badRequest('Faltan datos obligatorios para COMPRA (serie, modelo, dot, profundidad, almacén)');
        }

        const existing = await tx.neumatico.findUnique({ where: { numero_serie } });
        if (existing) throw BusinessError.conflict(`El neumático ${numero_serie} ya existe`);

        // 1. Crear el Neumático
        const nuevoNeumatico = await tx.neumatico.create({
            data: {
                numero_serie,
                modelo_id,
                dot,
                profundidad_inicial_mm: profundidad_inicial,
                profundidad_actual_mm: profundidad_inicial,
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen_destino_id,
                fecha_compra: now,
                costo_compra: costo_compra ? new Prisma.Decimal(costo_compra) : undefined,
                creado_por: userId,
                activo: true
            }
        });

        // 2. Registrar el Evento
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.COMPRA,
                neumatico_id: nuevoNeumatico.id,
                fecha_evento: now,
                proveedor_id,
                almacen_destino_id,
                costo_evento: costo_compra ? new Prisma.Decimal(costo_compra) : undefined,
                profundidad_remanente: profundidad_inicial,
                notas: notas || 'Alta inicial por compra',
                creado_por: userId
            }
        });

        return { neumatico: nuevoNeumatico, evento: nuevoEvento };
    }

    private async _handleInstalacion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, vehiculo_id, posicion_montaje_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!neumatico_id || !vehiculo_id) throw BusinessError.badRequest('Faltan datos instalación');

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true });
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw BusinessError.conflict('El neumático no está en stock');

        const vehiculo = await tx.vehiculo.findUnique({ where: { id: vehiculo_id } });
        if (!vehiculo) throw BusinessError.notFound('Vehículo', vehiculo_id);

        // Validación de Posición
        if (posicion_montaje_id) {
            const posicion = await tx.posicionNeumatico.findUnique({ where: { id: posicion_montaje_id }, include: { configuracion_eje: true } });
            if (!posicion) throw BusinessError.notFound('Posición', posicion_montaje_id);
            if (posicion.configuracion_eje.tipo_vehiculo_id !== vehiculo.tipo_vehiculo_id) throw BusinessError.badRequest('Posición no corresponde al vehículo');
            if (neumatico.es_reencauchado && !posicion.configuracion_eje.permite_reencauchados) throw BusinessError.badRequest('Posición no permite reencauchados');

            const ocupada = await tx.neumatico.findFirst({ where: { ubicacion_posicion_id: posicion_montaje_id, activo: true, estado_actual: EstadoNeumaticoEnum.INSTALADO } });
            if (ocupada) throw BusinessError.conflict(`Posición ocupada por ${ocupada.numero_serie}`);
        }

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                neumatico_id, fecha_evento: now, kilometraje_vehiculo, profundidad_remanente, presion_psi, vehiculo_id, posicion_montaje_id, notas: observaciones, creado_por: userId
            }
        });

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
                actualizado_en: now
            }
        });

        await tx.historialEstadoNeumatico.create({
            data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: EstadoNeumaticoEnum.INSTALADO, fecha_cambio: now, motivo: `Montaje en ${vehiculo.placa}`, creado_por: userId }
        });

        if (kilometraje_vehiculo) {
            await tx.registroOdometro.create({ data: { vehiculo_id, kilometraje: kilometraje_vehiculo, fecha_registro: now, registrado_por: userId, notas: `Montaje ${neumatico.numero_serie}` } });
            await tx.vehiculo.update({ where: { id: vehiculo_id }, data: { kilometraje_actual: kilometraje_vehiculo } });
        }

        return nuevoEvento;
    }

    private async _handleDesmontaje(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, kilometraje_vehiculo, profundidad_remanente, presion_psi, observaciones, estado_neumatico_resultante, almacen_destino_id, motivo_desecho_id } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { ubicacion_vehiculo: true });
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw BusinessError.badRequest('Neumático no instalado');

        let kmRecorrido = 0;
        if (neumatico.fecha_instalacion && kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            const instEvento = await tx.eventoNeumatico.findFirst({ where: { neumatico_id, tipo_evento: TipoEventoNeumaticoEnum.INSTALACION }, orderBy: { fecha_evento: 'desc' } });
            if (instEvento?.kilometraje_vehiculo) {
                kmRecorrido = kilometraje_vehiculo - instEvento.kilometraje_vehiculo;
                if (kmRecorrido < 0) throw BusinessError.badRequest(`KM actual (${kilometraje_vehiculo}) menor al de instalación (${instEvento.kilometraje_vehiculo})`);
            }
        }

        const nuevoEstado = estado_neumatico_resultante || EstadoNeumaticoEnum.EN_STOCK;
        if (nuevoEstado === EstadoNeumaticoEnum.EN_STOCK && !almacen_destino_id) throw BusinessError.badRequest('Requiere almacén destino');
        if (nuevoEstado === EstadoNeumaticoEnum.DESECHADO && !motivo_desecho_id) throw BusinessError.badRequest('Requiere motivo desecho');

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.DESMONTAJE,
                neumatico_id, fecha_evento: now, kilometraje_vehiculo, profundidad_remanente, presion_psi, vehiculo_id: neumatico.ubicacion_vehiculo_id, posicion_montaje_id: neumatico.ubicacion_posicion_id, almacen_destino_id, motivo_desecho_id, notas: observaciones, creado_por: userId
            }
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: nuevoEstado,
                ubicacion_almacen_id: almacen_destino_id || null,
                ubicacion_vehiculo_id: null,
                ubicacion_posicion_id: null,
                profundidad_actual_mm: profundidad_remanente,
                presion_actual_psi: presion_psi,
                kilometraje_acumulado: { increment: kmRecorrido },
                fecha_desecho: nuevoEstado === EstadoNeumaticoEnum.DESECHADO ? now : null,
                actualizado_en: now
            }
        });

        await tx.historialEstadoNeumatico.create({
            data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: nuevoEstado, fecha_cambio: now, motivo: 'Desmontaje', creado_por: userId }
        });

        if (kilometraje_vehiculo && neumatico.ubicacion_vehiculo_id) {
            await tx.registroOdometro.create({ data: { vehiculo_id: neumatico.ubicacion_vehiculo_id, kilometraje: kilometraje_vehiculo, fecha_registro: now, registrado_por: userId, notas: `Desmontaje ${neumatico.numero_serie}` } });
            await tx.vehiculo.update({ where: { id: neumatico.ubicacion_vehiculo_id }, data: { kilometraje_actual: kilometraje_vehiculo } });
        }

        return nuevoEvento;
    }

    private async _handleInspeccion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, profundidad_remanente, presion_psi, kilometraje_vehiculo, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        await this._validateAndGetNeumatico(tx, neumatico_id);

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
                neumatico_id, fecha_evento: now, kilometraje_vehiculo, profundidad_remanente, presion_psi, notas: observaciones, creado_por: userId
            }
        });

        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                profundidad_actual_mm: profundidad_remanente ?? undefined,
                presion_actual_psi: presion_psi ?? undefined,
                actualizado_en: now
            }
        });
        return nuevoEvento;
    }

    private async _handleRotacion(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, posicion_montaje_id, kilometraje_vehiculo, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        if (!posicion_montaje_id) throw BusinessError.badRequest('Falta posición destino');
        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true });
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) throw BusinessError.badRequest('Neumático no instalado');

        const origenPosId = neumatico.ubicacion_posicion_id;
        const destinoPosId = posicion_montaje_id;

        const targetPos = await tx.posicionNeumatico.findUnique({ where: { id: destinoPosId }, include: { configuracion_eje: true } });
        if (!targetPos) throw BusinessError.notFound('Posición destino', destinoPosId);
        if (neumatico.es_reencauchado && !targetPos.configuracion_eje.permite_reencauchados) throw BusinessError.badRequest('Destino no permite reencauchados');

        const neumáticoEnDestino = await tx.neumatico.findFirst({
            where: { ubicacion_posicion_id: destinoPosId, activo: true, estado_actual: EstadoNeumaticoEnum.INSTALADO }
        });

        if (neumáticoEnDestino && origenPosId) {
            const origenPos = await tx.posicionNeumatico.findUnique({ where: { id: origenPosId }, include: { configuracion_eje: true } });
            if (neumáticoEnDestino.es_reencauchado && !origenPos?.configuracion_eje.permite_reencauchados) throw BusinessError.badRequest('Swap inválido: reencauchado a origen prohibido');
        }

        const eventoRotacion = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
                neumatico_id, fecha_evento: now, kilometraje_vehiculo, vehiculo_id: neumatico.ubicacion_vehiculo_id, posicion_montaje_id: destinoPosId, notas: observaciones, creado_por: userId
            }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { ubicacion_posicion_id: destinoPosId, actualizado_en: now } });

        if (neumáticoEnDestino && origenPosId) {
            await tx.eventoNeumatico.create({
                data: { tipo_evento: TipoEventoNeumaticoEnum.ROTACION, neumatico_id: neumáticoEnDestino.id, fecha_evento: now, kilometraje_vehiculo, vehiculo_id: neumatico.ubicacion_vehiculo_id, posicion_montaje_id: origenPosId, notas: `Intercambio con ${neumatico.numero_serie}`, creado_por: userId }
            });
            await tx.neumatico.update({ where: { id: neumáticoEnDestino.id }, data: { ubicacion_posicion_id: origenPosId, actualizado_en: now } });
        }
        return eventoRotacion;
    }

    private async _handleReparacionEntrada(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw BusinessError.badRequest('Debe estar en STOCK');

        await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REPARACION_ENTRADA, neumatico_id, fecha_evento: now, proveedor_id, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { estado_actual: EstadoNeumaticoEnum.EN_REPARACION, ubicacion_almacen_id: null, actualizado_en: now } });
        await tx.historialEstadoNeumatico.create({ data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: EstadoNeumaticoEnum.EN_REPARACION, fecha_cambio: now, motivo: 'Envío reparación', creado_por: userId } });
    }

    private async _handleReparacionSalida(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REPARACION) throw BusinessError.badRequest('No está en reparación');

        // ✅ FIX 2: Registro de costo para trazabilidad financiera
        const nuevoEvento = await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REPARACION_SALIDA, neumatico_id, fecha_evento: now, almacen_destino_id, costo_evento: costo_evento ? new Prisma.Decimal(costo_evento) : undefined, profundidad_remanente, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { estado_actual: EstadoNeumaticoEnum.EN_STOCK, ubicacion_almacen_id: almacen_destino_id, profundidad_actual_mm: profundidad_remanente, actualizado_en: now } });
        await tx.historialEstadoNeumatico.create({ data: { neumatico_id, estado_anterior: EstadoNeumaticoEnum.EN_REPARACION, estado_nuevo: EstadoNeumaticoEnum.EN_STOCK, fecha_cambio: now, motivo: 'Retorno reparación', creado_por: userId } });
        return nuevoEvento;
    }

    private async _handleReencaucheEntrada(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, proveedor_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id, { modelo: true });
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) throw BusinessError.badRequest('Debe estar en STOCK');

        // Validación de Tipo (Casteo seguro gracias a Prisma)
        const modelo = neumatico.modelo as any; // Prisma lo trae, pero forzamos acceso por si acaso
        if (modelo && neumatico.reencauches_realizados >= modelo.reencauches_maximos) throw BusinessError.conflict(`Límite reencauches alcanzado (${modelo.reencauches_maximos})`);

        await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_ENTRADA, neumatico_id, fecha_evento: now, proveedor_id, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { estado_actual: EstadoNeumaticoEnum.EN_REENCAUCHE, ubicacion_almacen_id: null, actualizado_en: now } });
        await tx.historialEstadoNeumatico.create({ data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: EstadoNeumaticoEnum.EN_REENCAUCHE, fecha_cambio: now, motivo: 'Envío reencauche', creado_por: userId } });
    }

    private async _handleReencaucheSalida(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, almacen_destino_id, costo_evento, observaciones, profundidad_remanente } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_REENCAUCHE) throw BusinessError.badRequest('No está en reencauche');

        const nuevoEvento = await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA, neumatico_id, fecha_evento: now, almacen_destino_id, costo_evento: costo_evento ? new Prisma.Decimal(costo_evento) : undefined, profundidad_remanente, notas: observaciones, creado_por: userId }
        });

        // ✅ FIX CRÍTICO 3: Reset de Ciclo de Vida para Cálculo de CPK correcto
        await tx.neumatico.update({
            where: { id: neumatico_id },
            data: {
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                ubicacion_almacen_id: almacen_destino_id,
                profundidad_actual_mm: profundidad_remanente,
                profundidad_inicial_mm: profundidad_remanente, // Nuevo inicio
                kilometraje_acumulado: 0, // Reset para nueva vida
                es_reencauchado: true,
                reencauches_realizados: { increment: 1 },
                actualizado_en: now
            }
        });

        await tx.historialEstadoNeumatico.create({ data: { neumatico_id, estado_anterior: EstadoNeumaticoEnum.EN_REENCAUCHE, estado_nuevo: EstadoNeumaticoEnum.EN_STOCK, fecha_cambio: now, motivo: 'Retorno reencauche (Nueva Vida)', creado_por: userId } });
        return nuevoEvento;
    }

    private async _handleDesecho(evento: EventoNeumaticoCreate, userId: string, tx: TxClient) {
        const { neumatico_id, motivo_desecho_id, observaciones } = evento;
        const now = new Date(evento.fecha_evento || new Date());

        const neumatico = await this._validateAndGetNeumatico(tx, neumatico_id);
        if (neumatico.estado_actual === EstadoNeumaticoEnum.INSTALADO) throw BusinessError.badRequest('Desmontar antes de desechar');

        await tx.eventoNeumatico.create({
            data: { tipo_evento: TipoEventoNeumaticoEnum.DESECHO, neumatico_id, fecha_evento: now, motivo_desecho_id, notas: observaciones, creado_por: userId }
        });

        await tx.neumatico.update({ where: { id: neumatico_id }, data: { estado_actual: EstadoNeumaticoEnum.DESECHADO, ubicacion_almacen_id: null, ubicacion_vehiculo_id: null, ubicacion_posicion_id: null, fecha_desecho: now, actualizado_en: now } });
        await tx.historialEstadoNeumatico.create({ data: { neumatico_id, estado_anterior: neumatico.estado_actual, estado_nuevo: EstadoNeumaticoEnum.DESECHADO, fecha_cambio: now, motivo: 'Baja definitiva', creado_por: userId } });
    }
}
