import { FabricanteNeumatico } from '@prisma/client';

export type FabricanteEntity = FabricanteNeumatico & {
    _count?: {
        modelos: number;
    };
};

export interface CreateFabricanteDTO {
    nombre: string;
    codigoAbreviado?: string;
    paisOrigen?: string;
    sitioWeb?: string;
}

export interface UpdateFabricanteDTO extends Partial<CreateFabricanteDTO> {
    activo?: boolean;
}

export interface FabricanteResponse {
    id: string;
    nombre: string;
    codigoAbreviado: string | null;
    paisOrigen: string | null;
    sitioWeb: string | null;
    totalModelos?: number;
    activo: boolean;
    createdAt: string;
    updatedAt: string | null;
}
