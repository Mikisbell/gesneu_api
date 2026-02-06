/**
 * Almacen Types - Simple Catalog Architecture
 * 
 * Este módulo define los tipos para la entidad Almacen.
 * Al ser un "Catálogo Simple", simplificamos la arquitectura:
 * - Entity y Response pueden ser muy similares.
 * - Branded IDs siguen siendo obligatorios.
 */

import { Prisma } from '@prisma/client';
import { AlmacenId, EmpresaId } from '../branded.types';

// ============================================
// 1. ENTITY (Prisma)
// ============================================

export type AlmacenEntity = Prisma.AlmacenGetPayload<{}>;

// ============================================
// 2. DTOs (Input)
// ============================================

// ============================================
// 2. DTOs (Input)
// ============================================

export interface CreateAlmacenDTO {
    codigo: string;
    nombre: string;
    tipo?: string;
    direccion?: string;
    activo?: boolean;
}

export interface UpdateAlmacenDTO extends Partial<CreateAlmacenDTO> { }

// ============================================
// 3. RESPONSE (Output)
// ============================================

export interface AlmacenResponse {
    id: AlmacenId;
    codigo: string;
    nombre: string;
    tipo: string | null;
    direccion: string | null;
    activo: boolean;
    createdAt: string;
    updatedAt: string;
}

// ============================================
// 4. VIEWMODEL (UI)
// ============================================

export interface AlmacenListItem {
    id: AlmacenId;
    displayName: string; // "Bodega Central (BOD-01)"
    ubicacion: string;
    activo: boolean;
    totalNeumaticos?: number; // Opcional, si se carga con conteos
}
