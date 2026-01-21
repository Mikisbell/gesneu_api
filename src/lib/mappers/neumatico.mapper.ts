/**
 * Neumatico Mappers - Transformaciones entre Capas
 * 
 * Este módulo contiene funciones puras que transforman objetos
 * entre las diferentes capas de la aplicación:
 * - DTO → Prisma Input
 * - Entity → Response
 * - Response → ViewModel
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { Prisma } from '@prisma/client';
// Trigger HMR rebuild - Force Cache Clear
import {
    NeumaticoEntity,
    NeumaticoResponse,
    CreateNeumaticoDTO,
    UpdateNeumaticoDTO,
    NeumaticoCardViewModel,
} from '@/types/domain/neumatico.types';
import {
    asNeumaticoId,
    asAlmacenId,
    asVehiculoId,
} from '@/types/branded.types';

// HOTFIX: Server cache is stale. Defining local helper to bypass import error.
const asPosicionNeumaticoId = (id: string) => id as any;

// ============================================
// DTO → PRISMA INPUT
// ============================================

/**
 * Transforma un DTO de creación al formato esperado por Prisma.
 * Maneja la lógica de ubicación inicial (Almacén vs Vehículo).
 */
export function mapDtoToPrismaCreate(dto: CreateNeumaticoDTO): Prisma.NeumaticoCreateInput {
    // Definir estado inicial basado en ubicación
    let estadoActual: any = 'EN_STOCK';
    if (dto.ubicacion_vehiculo_id) {
        estadoActual = 'MONTADO';
    }

    const input: Prisma.NeumaticoCreateInput = {
        numero_serie: dto.numero_serie,
        dot: dto.dot,
        estado_actual: dto.estado === 'REENCAUCHADO' ? estadoActual : estadoActual, // Si es reencauchado, mantiene ub
        es_reencauchado: dto.estado === 'REENCAUCHADO',

        // Costos y Compras
        costo_compra: dto.costo_compra,
        moneda_compra: dto.moneda_compra ?? 'PEN',
        fecha_compra: dto.fecha_compra ?? new Date(),
        fecha_fabricacion: dto.fecha_fabricacion,

        // Mediciones Iniciales
        profundidad_remanente_actual_mm: dto.profundidad_inicial ?? 0, // Se actualizará con modelo
        profundidad_inicial_mm: dto.profundidad_inicial,
        kilometraje_acumulado: dto.kilometraje_acumulado ?? 0,

        // Relaciones
        modelo: { connect: { id: dto.modelo_id } },
    };

    // Proveedor opcional
    if (dto.proveedor_id) {
        input.proveedor_compra = { connect: { id: dto.proveedor_id } };
    }

    // Lógica Ubicación: Exclusividad Almacén vs Vehículo
    if (dto.ubicacion_almacen_id) {
        input.ubicacion_almacen = { connect: { id: dto.ubicacion_almacen_id } };
        // Limpiar otros
        input.ubicacion_vehiculo = undefined;
        input.ubicacion_posicion = undefined;
    } else if (dto.ubicacion_vehiculo_id && dto.ubicacion_posicion_id) {
        input.ubicacion_vehiculo = { connect: { id: dto.ubicacion_vehiculo_id } };
        input.ubicacion_posicion = { connect: { id: dto.ubicacion_posicion_id } };
        // Limpiar almacén
        input.ubicacion_almacen = undefined;
    }

    return input;
}

/**
 * Transforma un DTO de actualización.
 */
export function mapDtoToPrismaUpdate(dto: UpdateNeumaticoDTO): Prisma.NeumaticoUpdateInput {
    const update: Prisma.NeumaticoUpdateInput = {};

    if (dto.numero_serie !== undefined) update.numero_serie = dto.numero_serie;
    if (dto.dot !== undefined) update.dot = dto.dot;
    if (dto.costo_compra !== undefined) update.costo_compra = dto.costo_compra;
    if (dto.fecha_compra !== undefined) update.fecha_compra = dto.fecha_compra;
    if (dto.fecha_fabricacion !== undefined) update.fecha_fabricacion = dto.fecha_fabricacion;
    if (dto.sensor_id !== undefined) update.sensor_id = dto.sensor_id;
    // if (dto.notas !== undefined) update.notas = dto.notas; // Property 'notas' does not exist in Prisma schema
    if (dto.activo !== undefined) update.activo = dto.activo;

    if (dto.proveedor_id !== undefined) {
        update.proveedor_compra = { connect: { id: dto.proveedor_id } };
    }

    return update;
}

// ============================================
// ENTITY → RESPONSE
// ============================================

/**
 * Transforma una Entity de Prisma al formato de respuesta de la API.
 */
export function mapEntityToResponse(entity: NeumaticoEntity): NeumaticoResponse {
    const e = entity as any;

    // Calcular ubicación legible
    let ubicacionTexto = 'No asignado';
    if (e.ubicacion_almacen) {
        ubicacionTexto = `Almacén: ${e.ubicacion_almacen.nombre}`;
    } else if (e.ubicacion_vehiculo && e.ubicacion_posicion) {
        ubicacionTexto = `${e.ubicacion_vehiculo.placa} - Pos ${e.ubicacion_posicion.codigo_posicion}`;
    }

    return {
        id: asNeumaticoId(e.id),
        identificacion: {
            serie: e.numero_serie ?? null,
            dot: e.dot ?? null,
            marca: e.modelo?.fabricante?.nombre ?? 'Desconocida',
            modelo: e.modelo?.nombre_modelo ?? 'Desconocido', // nombre_modelo en DB
            medida: e.modelo?.medida ?? 'N/A',
            diseno: e.modelo?.patron_dibujo ?? null,
        },
        estado: {
            condicion: e.es_reencauchado ? 'REENCAUCHADO' : (e.estado_actual === 'DESECHO' ? 'DESECHO' : (e.kilometraje_acumulado > 0 ? 'USADO' : 'NUEVO')),
            estadoActual: e.estado_actual,
            ubicacion: ubicacionTexto,
            esReencauchado: e.es_reencauchado,
            vidaActual: e.vida_actual,
        },
        mediciones: {
            profundidadRemanente: Number(e.profundidad_remanente_actual_mm ?? 0),
            presion: e.presion_actual_psi ? Number(e.presion_actual_psi) : null,
            kilometrajeAcumulado: Number(e.kilometraje_acumulado ?? 0),
            horasAcumuladas: Number(e.horas_acumuladas ?? 0),
        },
        costos: {
            valorCompra: e.costo_compra ? Number(e.costo_compra) : null,
            moneda: e.moneda_compra,
            proveedor: e.proveedor_compra?.nombre_comercial ?? null,
        },
        fechas: {
            compra: e.fecha_compra?.toISOString() ?? null,
            fabricacion: e.fecha_fabricacion?.toISOString() ?? null,
            ultimoEvento: e.fecha_ultimo_evento?.toISOString() ?? null,
        },
        ubicacion: {
            almacenId: e.ubicacion_almacen_id ? asAlmacenId(e.ubicacion_almacen_id) : null,
            vehiculoId: e.ubicacion_vehiculo_id ? asVehiculoId(e.ubicacion_vehiculo_id) : null,
            posicionId: e.ubicacion_posicion_id ? asPosicionNeumaticoId(e.ubicacion_posicion_id) : null,
        },
        activo: e.activo,
        createdAt: e.creado_en?.toISOString() ?? new Date().toISOString(),
        updatedAt: e.actualizado_en?.toISOString() ?? new Date().toISOString(),
    };
}

// ============================================
// RESPONSE → VIEWMODEL
// ============================================

export function mapResponseToCardViewModel(response: NeumaticoResponse): NeumaticoCardViewModel {
    const isMontado = response.estado.estadoActual === 'MONTADO';
    const isAlmacen = response.estado.estadoActual === 'EN_STOCK';

    return {
        id: response.id,
        displayName: `${response.identificacion.marca} ${response.identificacion.modelo} - ${response.identificacion.serie || response.identificacion.dot || 'S/N'}`,
        ubicacionBadge: {
            label: response.estado.ubicacion,
            color: isMontado ? 'blue' : (isAlmacen ? 'purple' : 'gray'),
        },
        condicionBadge: {
            label: response.estado.condicion,
            color: response.estado.condicion === 'NUEVO' ? 'green' : 'orange',
        },
        remanente: {
            valor: response.mediciones.profundidadRemanente,
            color: response.mediciones.profundidadRemanente > 5 ? 'green' : (response.mediciones.profundidadRemanente > 2 ? 'yellow' : 'red'),
        },
        km: `${response.mediciones.kilometrajeAcumulado.toLocaleString()} km`,
        costoKm: '$0.00 / km', // Pendiente de implementar cálculo real
    };
}

// ============================================
// BATCH MAPPERS
// ============================================

export function mapEntitiesToResponses(entities: NeumaticoEntity[]): NeumaticoResponse[] {
    return entities.map(mapEntityToResponse);
}
