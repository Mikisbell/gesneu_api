
import { ModeloNeumatico, FabricanteNeumatico } from '@prisma/client';

export type ModeloNeumaticoEntity = ModeloNeumatico & {
    fabricante: FabricanteNeumatico;
};

export interface CreateModeloNeumaticoDTO {
    fabricante_id: string;
    nombre: string;
    medida: string;
    profundidad_original_mm: number;
    presion_recomendada_psi?: number;
    indice_carga?: string;
    indice_velocidad?: string;
    permite_reencauche?: boolean;
    reencauches_maximos?: number;
    // Others omitted for Phase 1
}

export interface UpdateModeloNeumaticoDTO extends Partial<CreateModeloNeumaticoDTO> {
    activo?: boolean;
}

export interface ModeloNeumaticoResponse {
    id: string;
    fabricante: {
        id: string;
        nombre: string;
    };
    nombre: string;
    medida: string;
    profundidadOriginal: number;
    presionRecomendada: number | null;
    especificaciones: {
        indiceCarga: string | null;
        indiceVelocidad: string | null;
    };
    reencauche: {
        permitido: boolean;
        maximos: number;
    };
    activo: boolean;
    createdAt: string;
    updatedAt: string | null;
}
