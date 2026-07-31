import { Prisma } from '@prisma/client';
import { AlmacenId, EmpresaId } from '../branded.types';

export type AlmacenEntity = Prisma.AlmacenGetPayload<{
    include?: {
        _count?: {
            select: { neumaticos: true }
        }
    }
}>;

export interface CreateAlmacenDTO {
    codigo: string;
    nombre: string;
    tipo?: string;
    direccion?: string;
    activo?: boolean;
}

export interface UpdateAlmacenDTO extends Partial<CreateAlmacenDTO> { }

export interface AlmacenResponse {
    id: AlmacenId;
    codigo: string;
    nombre: string;
    tipo: string | null;
    direccion: string | null;
    totalNeumaticos?: number;
    activo: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface AlmacenListItem {
    id: AlmacenId;
    displayName: string;
    ubicacion: string;
    activo: boolean;
    totalNeumaticos?: number;
}
