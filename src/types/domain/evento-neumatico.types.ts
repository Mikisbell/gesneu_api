/**
 * EventoNeumatico Types - Arquitectura Híbrida
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { Prisma } from '@prisma/client';
import {
    EventoId,
    NeumaticoId,
    VehiculoId,
    UsuarioId,
    AlmacenId,
    ProveedorId
} from '../branded.types';

// ============================================
// 1. ENTITY (Prisma/BD)
// ============================================
export type EventoNeumaticoEntity = Prisma.EventoNeumaticoGetPayload<{
    include: {
        neumatico: {
            include: {
                modelo: {
                    include: {
                        fabricante: true;
                    }
                }
            }
        };
        vehiculo: true;
        posicion_montaje: true;
        almacen_destino: true;
        proveedor: true;
        motivo_desecho: true;
        usuario: true; // Creado por
    }
}>;

// ============================================
// 2. DTOs (INPUTS)
// ============================================
// SE IMPORTAN DIRECTAMENTE DEL VALIDATOR (Enfoque Híbrido)
// import { CreateEventoInput } from '@/lib/validators/evento-neumatico';


// ============================================
// 3. RESPONSE (OUTPUTS)
// ============================================
export interface EventoResponse {
    id: EventoId;
    tipo: string; // "INSTALACION", "ROTACION"
    fecha: string; // ISO

    // Contexto del Neumático en ese momento
    neumatico: {
        id: NeumaticoId;
        serie: string;
        marca: string;
        modelo: string;
    };

    // Detalles Operativos
    costo: number | null;
    observaciones: string | null;

    // Datos de Vida
    contadores: {
        kmVehiculo: number | null;
        remanenteMm: number | null; // Promedio o min
        presionPsi: number | null;
    };

    // Relaciones (Opcionales según tipo)
    destino: {
        vehiculo: { id: VehiculoId; placa: string } | null;
        posicion: string | null; // Código de posición
        almacen: { id: AlmacenId; nombre: string } | null;
        proveedor: { id: ProveedorId; nombre: string } | null;
    };

    autor: {
        id: UsuarioId | null;
        nombre: string | null;
    };

    createdAt: string;
}
