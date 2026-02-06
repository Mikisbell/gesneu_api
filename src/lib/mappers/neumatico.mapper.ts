
import { Prisma } from '@prisma/client';
import { CreateNeumaticoDTO, UpdateNeumaticoDTO, NeumaticoEntity, NeumaticoResponse } from '@/types/domain/neumatico.types';

export function mapDtoToPrismaCreate(dto: CreateNeumaticoDTO, userId: string, empresaId: string): Prisma.NeumaticoCreateInput {
    // Basic mapping. 
    // Relations (Modelo, Proveedor, Almacen) must be connected.
    // Dates need parsing if string.

    const data: Prisma.NeumaticoCreateInput = {
        empresa: { connect: { id: empresaId } },
        modelo: { connect: { id: dto.modelo_id } },
        numero_serie: dto.numero_serie,
        dot: dto.dot,
        sensor_id: dto.sensor_id,
        es_reencauchado: dto.es_reencauchado,

        fecha_compra: new Date(dto.fecha_compra),
        fecha_fabricacion: dto.fecha_fabricacion ? new Date(dto.fecha_fabricacion) : undefined,
        costo_compra: dto.costo_compra,
        moneda_compra: dto.moneda_compra,

        profundidad_inicial_mm: dto.profundidad_inicial_mm,
        profundidad_remanente_actual_mm: dto.profundidad_actual_mm,
        profundidad_int: dto.profundidad_int,
        profundidad_cen: dto.profundidad_cen,
        profundidad_ext: dto.profundidad_ext,
        presion_actual_psi: dto.presion_actual_psi,

        creado_por: userId,
        activo: true,
    };

    if (dto.proveedor_compra_id) {
        data.proveedor_compra = { connect: { id: dto.proveedor_compra_id } };
    }

    if (dto.ubicacion_almacen_id) {
        data.ubicacion_almacen = { connect: { id: dto.ubicacion_almacen_id } };
        data.estado_actual = 'EN_STOCK'; // Default state in Almacen
    }

    return data;
}

export function mapDtoToPrismaUpdate(dto: UpdateNeumaticoDTO, userId: string): Prisma.NeumaticoUpdateInput {
    const data: Prisma.NeumaticoUpdateInput = {
        actualizado_por: userId,
        actualizado_en: new Date()
    };

    if (dto.numero_serie !== undefined) data.numero_serie = dto.numero_serie;
    if (dto.dot !== undefined) data.dot = dto.dot;
    if (dto.sensor_id !== undefined) data.sensor_id = dto.sensor_id;
    if (dto.activo !== undefined) data.activo = dto.activo;

    return data;
}

export function mapEntityToResponse(entity: NeumaticoEntity): NeumaticoResponse {
    let ubicacionTipo: NeumaticoResponse['ubicacion']['tipo'] = 'DESCONOCIDO';
    if (entity.ubicacion_almacen_id) ubicacionTipo = 'ALMACEN';
    else if (entity.ubicacion_vehiculo_id) ubicacionTipo = 'VEHICULO';
    else if (entity.motivo_desecho_id) ubicacionTipo = 'DESECHO'; // implied state

    return {
        id: entity.id,
        numeroSerie: entity.numero_serie,
        codigo: entity.numero_serie ?? 'S/N', // Fallback
        deviceId: entity.sensor_id,
        dot: entity.dot,
        estado: entity.estado_actual,

        modelo: {
            id: entity.modelo?.id ?? '',
            nombre: entity.modelo?.nombre_modelo ?? 'Desconocido',
            medida: entity.modelo?.medida ?? '',
            fabricante: {
                id: entity.modelo?.fabricante.id ?? '',
                nombre: entity.modelo?.fabricante.nombre ?? ''
            }
        },

        condicion: {
            esReencauchado: entity.es_reencauchado,
            reencauchesRealizados: entity.reencauches_realizados,
            vidaActual: entity.vida_actual
        },

        mediciones: {
            profundidadActual: Number(entity.profundidad_remanente_actual_mm),
            profundidadInicial: entity.profundidad_inicial_mm ? Number(entity.profundidad_inicial_mm) : null,
            presion: entity.presion_actual_psi ? Number(entity.presion_actual_psi) : null,
        },

        ubicacion: {
            tipo: ubicacionTipo,
            almacen: entity.ubicacion_almacen ? {
                id: entity.ubicacion_almacen.id,
                nombre: entity.ubicacion_almacen.nombre
            } : undefined,
            vehiculo: entity.ubicacion_vehiculo ? {
                id: entity.ubicacion_vehiculo.id,
                placa: entity.ubicacion_vehiculo.placa ?? 'SIN-PLACA'
            } : undefined,
            posicion: entity.ubicacion_posicion ? {
                id: entity.ubicacion_posicion.id,
                codigo: entity.ubicacion_posicion.codigo_posicion
            } : undefined
        },

        compra: {
            fecha: entity.fecha_compra.toISOString(),
            costo: entity.costo_compra ? Number(entity.costo_compra) : null,
            moneda: entity.moneda_compra,
            proveedorId: entity.proveedor_compra_id
        },

        estadisticas: {
            kmAcumulados: Number(entity.kilometraje_acumulado),
            horasAcumuladas: Number(entity.horas_acumuladas),
            costoPorKm: null, // To be implemented or removed
            proximaInspeccionKm: entity.proxima_inspeccion_km ? Number(entity.proxima_inspeccion_km) : null,
            proximaInspeccionFecha: entity.proxima_inspeccion_fecha?.toISOString() ?? null
        },

        createdAt: entity.creado_en.toISOString(),
        updatedAt: entity.actualizado_en?.toISOString() ?? null
    };
}
