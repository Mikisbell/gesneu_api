/**
 * Vehiculo Mappers - Transformaciones entre Capas
 * 
 * Este módulo contiene funciones puras que transforman objetos
 * entre las diferentes capas de la aplicación:
 * - DTO → Prisma Input
 * - Entity → Response
 * - Response → ViewModel
 * 
 * REGLA: Nunca pasar objetos directamente de una capa a otra.
 * Siempre usar un mapper.
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { Prisma } from '@prisma/client';
import {
    CreateVehiculoDTO,
    UpdateVehiculoDTO,
    VehiculoEntity,
    VehiculoResponse,
    VehiculoListItem,
    VehiculoCardViewModel,
    VehiculoFormViewModel,
    NeumaticoInstalado,
    TipoVehiculoResponse,
} from '@/types/domain/vehiculo.types';
import { asVehiculoId, asTipoVehiculoId, asNeumaticoId, VehiculoId } from '@/types/branded.types';

// ============================================
// DTO → PRISMA INPUT
// ============================================

/**
 * Transforma un DTO de creación al formato esperado por Prisma.
 * Maneja el mapeo de nombres de campos y la conexión de relaciones.
 */
export function mapDtoToPrismaCreate(dto: CreateVehiculoDTO): Prisma.VehiculoCreateInput {
    return {
        placa: dto.placa,
        marca: dto.marca,
        modelo_vehiculo: dto.modelo,
        anio_fabricacion: dto.anio,
        odometro_actual: dto.odometro_actual ?? dto.kilometraje_actual ?? 0,
        tipo_medicion: dto.tipo_medicion ?? 'KILOMETRAJE',
        vin: dto.chasis_serie ?? null,
        numero_economico: dto.numero_economico ?? generateNumeroEconomico(dto.placa),
        activo: dto.activo ?? true,
        tipo_vehiculo: {
            connect: { id: dto.tipo_vehiculo_id },
        },
    };
}

/**
 * Transforma un DTO de actualización al formato esperado por Prisma.
 * Solo incluye campos que fueron proporcionados (no undefined).
 */
export function mapDtoToPrismaUpdate(dto: UpdateVehiculoDTO): Prisma.VehiculoUpdateInput {
    const updateData: Prisma.VehiculoUpdateInput = {};

    // Campos escalares directos
    if (dto.placa !== undefined) {
        updateData.placa = dto.placa;
    }
    if (dto.marca !== undefined) {
        updateData.marca = dto.marca;
    }
    if (dto.numero_economico !== undefined) {
        updateData.numero_economico = dto.numero_economico;
    }
    if (dto.tipo_medicion !== undefined) {
        updateData.tipo_medicion = dto.tipo_medicion;
    }
    if (dto.activo !== undefined) {
        updateData.activo = dto.activo;
    }

    // Campos con mapeo de nombres
    if (dto.modelo !== undefined) {
        updateData.modelo_vehiculo = dto.modelo;
    }
    if (dto.anio !== undefined) {
        updateData.anio_fabricacion = dto.anio;
    }
    if (dto.chasis_serie !== undefined) {
        updateData.vin = dto.chasis_serie;
    }

    // Odómetro: priorizar odometro_actual, luego kilometraje_actual
    const odometro = dto.odometro_actual ?? dto.kilometraje_actual;
    if (odometro !== undefined) {
        updateData.odometro_actual = odometro;
    }

    // Relación tipo_vehiculo (requiere connect para updates)
    if (dto.tipo_vehiculo_id !== undefined) {
        updateData.tipo_vehiculo = {
            connect: { id: dto.tipo_vehiculo_id },
        };
    }

    return updateData;
}

// ============================================
// ENTITY → RESPONSE
// ============================================

/**
 * Transforma una Entity de Prisma al formato de respuesta de la API.
 * Normaliza nombres de campos y estructura las relaciones.
 */
export function mapEntityToResponse(entity: VehiculoEntity): VehiculoResponse {
    // Cast to any to handle dynamic schema, with safe fallbacks
    const e = entity as any;
    return {
        id: asVehiculoId(e.id),
        placa: e.placa ?? '',
        marca: e.marca ?? '',
        modelo: e.modelo_vehiculo ?? '',
        anio: e.anio_fabricacion ?? 0,
        vin: e.vin ?? null,
        numeroEconomico: e.numero_economico ?? '',
        kilometraje: e.odometro_actual ?? 0,
        tipoMedicion: (e.tipo_medicion ?? 'KILOMETRAJE') as 'KILOMETRAJE' | 'HOROMETRO',
        activo: e.activo ?? true,
        tipoVehiculo: mapTipoVehiculoToResponse(e.tipo_vehiculo),
        neumaticosInstalados: e.neumaticos_instalados?.map(mapNeumaticoInstalado) ?? [],
        // Vehiculo model uses fecha_alta instead of creado_en
        createdAt: e.fecha_alta?.toISOString?.() ?? new Date().toISOString(),
        updatedAt: e.fecha_alta?.toISOString?.() ?? new Date().toISOString(),
    } satisfies VehiculoResponse;
}

/**
 * Transforma el tipo de vehículo a formato de respuesta.
 */
function mapTipoVehiculoToResponse(tipoVehiculo: any): TipoVehiculoResponse {
    // TipoVehiculo doesn't have cantidad_ejes/cantidad_neumaticos directly,
    // they would need to be computed from configuraciones.length or summed.
    // For now, use safe defaults.
    return {
        id: asTipoVehiculoId(tipoVehiculo?.id ?? ''),
        nombre: tipoVehiculo?.nombre ?? 'N/A',
        cantidadEjes: tipoVehiculo?.configuraciones?.length ?? 0,
        cantidadNeumaticos: computeTotalNeumaticos(tipoVehiculo?.configuraciones),
    };
}

/**
 * Computes total tires from ConfiguracionEje array.
 */
function computeTotalNeumaticos(configuraciones: any[] | undefined): number {
    if (!configuraciones || configuraciones.length === 0) return 0;
    return configuraciones.reduce((sum: number, eje: any) => {
        return sum + (eje.numero_posiciones ?? 0) * (eje.neumaticos_por_posicion ?? 1);
    }, 0);
}

/**
 * Transforma un neumático instalado a formato de respuesta.
 */
function mapNeumaticoInstalado(neumatico: any): NeumaticoInstalado {
    return {
        id: asNeumaticoId(neumatico?.id ?? ''),
        numeroSerie: neumatico?.numero_serie ?? 'S/N',
        posicion: neumatico?.ubicacion_posicion?.codigo_posicion ?? 'N/A',
        // modelo is a relation with its own nombre field
        marca: neumatico?.modelo?.fabricante?.nombre ?? 'N/A',
        modelo: neumatico?.modelo?.nombre ?? 'N/A',
    };
}

/**
 * Transforma una Entity a un item de lista simplificado.
 */
export function mapEntityToListItem(entity: VehiculoEntity): VehiculoListItem {
    const e = entity as any;
    return {
        id: asVehiculoId(e.id),
        placa: e.placa ?? '',
        marca: e.marca ?? '',
        modelo: e.modelo_vehiculo ?? '',
        anio: e.anio_fabricacion ?? 0,
        tipoVehiculo: e.tipo_vehiculo?.nombre ?? 'N/A',
        neumaticosInstalados: e.neumaticos_instalados?.length ?? 0,
        neumaticosEsperados: computeTotalNeumaticos(e.tipo_vehiculo?.configuraciones),
        activo: e.activo ?? true,
    };
}

// ============================================
// RESPONSE → VIEWMODEL
// ============================================

/**
 * Transforma una Response al ViewModel para tarjetas de vehículos.
 */
export function mapResponseToCardViewModel(
    response: VehiculoResponse,
    alertCount: number = 0
): VehiculoCardViewModel {
    const instalados = response.neumaticosInstalados.length;
    const esperados = response.tipoVehiculo.cantidadNeumaticos;

    // Determinar color de estado
    let statusColor: 'green' | 'yellow' | 'red' = 'green';
    if (!response.activo) {
        statusColor = 'red';
    } else if (alertCount > 0) {
        statusColor = 'red';
    } else if (instalados < esperados) {
        statusColor = 'yellow';
    }

    return {
        id: response.id,
        displayName: `${response.marca} ${response.modelo} ${response.anio} - ${response.placa}`,
        statusColor,
        alertCount,
        neumaticosCount: `${instalados}/${esperados}`,
        lastUpdate: formatRelativeDate(response.updatedAt),
        tipoVehiculo: response.tipoVehiculo.nombre,
    };
}

/**
 * Transforma una Response al ViewModel de formulario de edición.
 */
export function mapResponseToFormViewModel(response: VehiculoResponse): VehiculoFormViewModel {
    return {
        id: response.id,
        placa: response.placa,
        marca: response.marca,
        modelo: response.modelo,
        anio: response.anio,
        tipoVehiculoId: response.tipoVehiculo.id,
        tipoMedicion: response.tipoMedicion,
        kilometraje: response.kilometraje,
        vin: response.vin ?? '',
        numeroEconomico: response.numeroEconomico,
        activo: response.activo,
    };
}

// ============================================
// HELPERS
// ============================================

/**
 * Genera un número económico a partir de la placa.
 * Usado cuando no se proporciona uno explícitamente.
 */
function generateNumeroEconomico(placa: string): string {
    return `ECO-${placa.replace(/[^A-Z0-9]/g, '')}`;
}

/**
 * Formatea una fecha ISO a un formato relativo.
 */
function formatRelativeDate(isoDate: string): string {
    const date = new Date(isoDate);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        if (diffHours === 0) {
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            return diffMinutes <= 1 ? 'Ahora mismo' : `Hace ${diffMinutes} minutos`;
        }
        return diffHours === 1 ? 'Hace 1 hora' : `Hace ${diffHours} horas`;
    }
    if (diffDays === 1) return 'Ayer';
    if (diffDays < 7) return `Hace ${diffDays} días`;
    if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
    return `Hace ${Math.floor(diffDays / 30)} meses`;
}

// ============================================
// BATCH MAPPERS
// ============================================

/**
 * Mapea múltiples entities a responses.
 */
export function mapEntitiesToResponses(entities: VehiculoEntity[]): VehiculoResponse[] {
    return entities.map(mapEntityToResponse);
}

/**
 * Mapea múltiples entities a items de lista.
 */
export function mapEntitiesToListItems(entities: VehiculoEntity[]): VehiculoListItem[] {
    return entities.map(mapEntityToListItem);
}
