/**
 * Neumatico Types - Arquitectura de Tipos por Capas
 * 
 * Este módulo define todos los tipos relacionados con la entidad Neumatico
 * siguiendo la arquitectura de 4 capas:
 * 1. Entity (Prisma/BD)
 * 2. DTOs (API Input)
 * 3. Response (API Output)
 * 4. ViewModel (UI)
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { Prisma } from '@prisma/client';
import {
    NeumaticoId,
    ModeloNeumaticoId,
    VehiculoId,
    AlmacenId,
    PosicionNeumaticoId,
    EmpresaId,
    ProveedorId
} from '../branded.types';

// ============================================
// 1. ENTITY (Lo que viene de Prisma/BD)
// ============================================

/**
 * Tipo de entidad Neumatico con relaciones incluidas.
 * Representa exactamente lo que Prisma devuelve de la base de datos.
 */
/**
 * Tipo de entidad Neumatico con relaciones incluidas.
 * Representa exactamente lo que Prisma devuelve de la base de datos.
 */
export type NeumaticoEntity = Prisma.NeumaticoGetPayload<{
    include: {
        modelo: {
            include: {
                fabricante: true;
            };
        };
        ubicacion_almacen: true;
        ubicacion_vehiculo: {
            include: {
                tipo_vehiculo: true;
            };
        };
        ubicacion_posicion: true;
        proveedor_compra: true;
        motivo_desecho: true;
    };
}>;

/**
 * Tipo de entidad Neumatico sin relaciones (solo campos escalares).
 */
export type NeumaticoScalarEntity = Prisma.NeumaticoGetPayload<object>;

/**
 * @deprecated Validar si esto se sigue usando. Preferir NeumaticoEntity.
 */
export interface INeumatico extends NeumaticoEntity { }

// ============================================
// 2. DTOs (Lo que recibe la API del cliente)
// ============================================

/**
 * DTO para creación de neumático.
 */
export interface CreateNeumaticoDTO {
    /** ID del modelo (catálogo) */
    modelo_id: string;
    /** Número de serie (opcional, algunos solo tienen DOT) */
    numero_serie?: string;
    /** DOT del neumático */
    dot?: string;
    /** Estado del neumático */
    estado?: 'NUEVO' | 'USADO' | 'REENCAUCHADO';
    /** Costo de compra */
    costo_compra?: number;
    moneda_compra?: string;
    /** ID del proveedor */
    proveedor_id?: string;
    /** Fecha de compra (ISO) */
    fecha_compra?: string;
    /** Fecha de fabricación (ISO) */
    fecha_fabricacion?: string;

    // Mediciones iniciales (para usados)
    profundidad_inicial?: number;
    kilometraje_acumulado?: number; // Para usados

    // Ubicación Inicial (Opcional, puede ir a almacén o vehículo)
    ubicacion_almacen_id?: string;
    ubicacion_vehiculo_id?: string;
    ubicacion_posicion_id?: string;
}

/**
 * DTO para actualización de neumático.
 * Limitado a correcciones de datos, no eventos de ciclo de vida.
 */
export interface UpdateNeumaticoDTO {
    numero_serie?: string;
    dot?: string;
    proveedor_id?: string;
    costo_compra?: number;
    fecha_compra?: string;
    fecha_fabricacion?: string;
    sensor_id?: string;
    notas?: string;
    activo?: boolean;
}

// ============================================
// 3. RESPONSE (Lo que devuelve la API)
// ============================================

/**
 * Respuesta de la API para un neumático.
 */
export interface NeumaticoResponse {
    id: NeumaticoId;
    identificacion: {
        serie: string | null;
        dot: string | null;
        marca: string;
        modelo: string;
        medida: string;
        diseno: string | null; // patron_dibujo
    };
    estado: {
        condicion: 'NUEVO' | 'USADO' | 'REENCAUCHADO' | 'DESECHO'; // Derivado
        estadoActual: string; // EN_STOCK, MONTADO, etc.
        ubicacion: string; // "Almacén Central" o "Vehículo ABC-123 Pos 1"
        esReencauchado: boolean;
        vidaActual: number;
    };
    mediciones: {
        profundidadRemanente: number; // mm
        presion: number | null; // psi
        kilometrajeAcumulado: number;
        horasAcumuladas: number;
    };
    costos: {
        valorCompra: number | null;
        moneda: string | null;
        proveedor: string | null;
    };
    fechas: {
        compra: string | null;
        fabricacion: string | null;
        ultimoEvento: string | null;
    };
    ubicacion: {
        almacenId: AlmacenId | null;
        vehiculoId: VehiculoId | null;
        posicionId: PosicionNeumaticoId | null;
    };
    activo: boolean;
    createdAt: string;
    updatedAt: string;
}

// ============================================
// 4. VIEWMODEL (Lo que usa React/UI)
// ============================================

export interface NeumaticoCardViewModel {
    id: NeumaticoId;
    displayName: string; // "Michelin XZE2 - SERIE123"
    ubicacionBadge: {
        label: string;
        color: 'blue' | 'purple' | 'gray'; // Almacen, Montado, Otro
    };
    condicionBadge: {
        label: string; // Nuevo vs Reencauchado
        color: 'green' | 'orange';
    };
    remanente: {
        valor: number; // mm
        color: 'green' | 'yellow' | 'red';
    };
    km: string; // Format "12,500 km"
    costoKm: string; // "$0.045 / km" (calculado)
}

// ============================================
// FILTROS
// ============================================

export interface NeumaticoFilters {
    serie?: string;
    marca?: string;
    estado?: string; // EN_STOCK, MONTADO
    ubicacion?: 'ALMACEN' | 'MONTADO';
    vehiculo_id?: string;
    search?: string;
}
