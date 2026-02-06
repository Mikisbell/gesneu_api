/**
 * Vehiculo Types - Arquitectura de Tipos por Capas
 * 
 * Este módulo define todos los tipos relacionados con la entidad Vehiculo
 * siguiendo la arquitectura de 4 capas:
 * 1. Entity (Prisma/BD)
 * 2. DTOs (API Input)
 * 3. Response (API Output)
 * 4. ViewModel (UI)
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { Prisma } from '@prisma/client';
import { VehiculoId, TipoVehiculoId, NeumaticoId } from '../branded.types';

// ============================================
// 1. ENTITY (Lo que viene de Prisma/BD)
// ============================================

/**
 * Tipo de entidad Vehiculo con relaciones incluidas.
 * Representa exactamente lo que Prisma devuelve de la base de datos.
 */
export type VehiculoEntity = Prisma.VehiculoGetPayload<{
    include: {
        tipo_vehiculo: true;
        neumaticos_instalados: {
            include: {
                modelo: {
                    include: {
                        fabricante: true;
                    };
                };
                ubicacion_posicion: true;
            };
        };
    };
}>;

/**
 * Tipo de entidad Vehiculo sin relaciones (solo campos escalares).
 */
export type VehiculoScalarEntity = Prisma.VehiculoGetPayload<object>;

/**
 * Tipo legacy para compatibilidad con código existente.
 * @deprecated Usar VehiculoEntity o VehiculoResponse en su lugar.
 */
export interface IVehiculo {
    id: string;
    tipo_vehiculo_id: string;
    placa: string | null;          // Nullable in Prisma schema
    vin: string | null;
    numero_economico: string;
    codigo_interno: string | null;
    marca: string | null;          // Nullable in Prisma schema
    modelo_vehiculo: string | null; // Nullable in Prisma schema
    anio_fabricacion: number | null; // Nullable in Prisma schema
    fecha_alta: Date;
    fecha_baja: Date | null;
    tipo_medicion: string;
    odometro_actual: number | null;
    fecha_ultimo_odometro: Date | null;
    peso_carga_maxima_diseno_ton: any; // Prisma Decimal type
    ubicacion_actual: string | null;
    centro_costo_id: string | null;
    ruta_id: string | null;
    empresa_id: string | null;
    notas: string | null;
    activo: boolean;
    version: number;
    tipo_vehiculo?: {
        id: string;
        nombre: string;
        cantidad_ejes?: number;
        cantidad_neumaticos?: number;
    };
    neumaticos_instalados?: {
        id: string;
        numero_serie: string | null;
        ubicacion_posicion?: {
            id: string;
            posicion_relativa?: number;
            codigo_posicion?: string;
            numero_posicion?: number;
        } | null;
    }[];
}

// ============================================
// 2. DTOs (Lo que recibe la API del cliente)
// ============================================

/**
 * DTO para creación de vehículo.
 * Usa nombres de campos amigables para el frontend.
 */
export interface CreateVehiculoDTO {
    /** Placa del vehículo (única) */
    placa: string;
    /** ID del tipo de vehículo (catálogo) */
    tipo_vehiculo_id: string;
    /** Marca del vehículo */
    marca: string;
    /** Modelo del vehículo (frontend usa 'modelo', BD usa 'modelo_vehiculo') */
    modelo: string;
    /** Año de fabricación (frontend usa 'anio', BD usa 'anio_fabricacion') */
    anio: number;
    /** Tipo de medición del contador */
    tipo_medicion?: 'KILOMETRAJE' | 'HOROMETRO';
    /** Kilometraje actual (frontend puede enviar 'kilometraje_actual', BD usa 'odometro_actual') */
    odometro_actual?: number;
    /** Alias: algunos frontends envían esto en lugar de odometro_actual */
    kilometraje_actual?: number;
    /** Número de serie del motor (no se guarda en BD actual) */
    motor_serie?: string;
    /** Número de chasis/VIN (frontend usa 'chasis_serie', BD usa 'vin') */
    chasis_serie?: string;
    /** Número económico interno */
    numero_economico?: string;
    /** Estado activo/inactivo */
    activo?: boolean;
}

/**
 * DTO para actualización de vehículo.
 * Todos los campos son opcionales.
 */
export interface UpdateVehiculoDTO {
    placa?: string;
    tipo_vehiculo_id?: string;
    marca?: string;
    modelo?: string;
    anio?: number;
    tipo_medicion?: 'KILOMETRAJE' | 'HOROMETRO';
    odometro_actual?: number;
    kilometraje_actual?: number;
    motor_serie?: string;
    chasis_serie?: string | null;  // Zod may output null
    numero_economico?: string;
    activo?: boolean;
}

// ============================================
// 3. RESPONSE (Lo que devuelve la API)
// ============================================

/**
 * Respuesta de la API para un vehículo.
 * Campos normalizados y amigables para el consumidor.
 */
export interface VehiculoResponse {
    id: VehiculoId;
    placa: string;
    marca: string;
    /** Modelo (renombrado de modelo_vehiculo) */
    modelo: string;
    /** Año (renombrado de anio_fabricacion) */
    anio: number;
    vin: string | null;
    numeroEconomico: string;
    /** Kilometraje/Horómetro (renombrado de odometro_actual) */
    kilometraje: number;
    tipoMedicion: 'KILOMETRAJE' | 'HOROMETRO';
    activo: boolean;
    tipoVehiculo: TipoVehiculoResponse;
    neumaticosInstalados: NeumaticoInstalado[];
    createdAt: string;
    updatedAt: string;
}

/**
 * Respuesta anidada de tipo de vehículo.
 */
export interface TipoVehiculoResponse {
    id: TipoVehiculoId;
    nombre: string;
    cantidadEjes: number;
    cantidadNeumaticos: number;
}

/**
 * Resumen de neumático instalado en un vehículo.
 */
export interface NeumaticoInstalado {
    id: NeumaticoId;
    numeroSerie: string;
    posicion: string;
    marca: string;
    modelo: string;
}

/**
 * Respuesta simplificada para listados.
 */
export interface VehiculoListItem {
    id: VehiculoId;
    placa: string;
    marca: string;
    modelo: string;
    anio: number;
    tipoVehiculo: string;
    neumaticosInstalados: number;
    neumaticosEsperados: number;
    activo: boolean;
}

// ============================================
// 4. VIEWMODEL (Lo que usa React/UI)
// ============================================

/**
 * ViewModel para tarjetas de vehículos en el dashboard.
 */
export interface VehiculoCardViewModel {
    id: VehiculoId;
    /** Nombre para mostrar: "Toyota Hilux 2024 - ABC-123" */
    displayName: string;
    /** Color del badge de estado */
    statusColor: 'green' | 'yellow' | 'red';
    /** Número de alertas activas */
    alertCount: number;
    /** Conteo de neumáticos: "8/8" */
    neumaticosCount: string;
    /** Última actualización relativa: "Hace 2 días" */
    lastUpdate: string;
    /** Tipo de vehículo para filtros */
    tipoVehiculo: string;
}

/**
 * ViewModel para el formulario de edición.
 */
export interface VehiculoFormViewModel {
    id?: VehiculoId;
    placa: string;
    marca: string;
    modelo: string;
    anio: number;
    tipoVehiculoId: TipoVehiculoId;
    tipoMedicion: 'KILOMETRAJE' | 'HOROMETRO';
    kilometraje: number;
    vin: string;
    numeroEconomico: string;
    activo: boolean;
}

// ============================================
// FILTROS
// ============================================

/**
 * Filtros de búsqueda para vehículos.
 */
export interface VehiculoFilters {
    placa?: string;
    tipo_vehiculo_id?: string;  // String from Zod, will be cast to TipoVehiculoId when needed
    marca?: string;
    activo?: boolean;
    /** Búsqueda de texto libre */
    search?: string;
    /** Multi-tenancy filter */
    empresa_id?: string;
}

// ============================================
// TIPOS AUXILIARES
// ============================================

/**
 * Estados posibles de un vehículo para badges.
 */
export type VehiculoStatus = 'operativo' | 'alerta' | 'inactivo';

/**
 * Opciones de ordenamiento para listados.
 */
export interface VehiculoSortOptions {
    field: 'placa' | 'marca' | 'anio' | 'createdAt';
    direction: 'asc' | 'desc';
}
