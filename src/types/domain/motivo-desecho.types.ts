
import { MotivoDesecho } from '@prisma/client';

export type MotivoDesechoEntity = MotivoDesecho;

export interface CreateMotivoDesechoDTO {
    codigo: string;
    nombre: string;
    descripcion?: string;
    requiere_evidencia?: boolean;
}

export interface UpdateMotivoDesechoDTO extends Partial<CreateMotivoDesechoDTO> {
    activo?: boolean;
}

export interface MotivoDesechoResponse {
    id: string;
    codigo: string;
    nombre: string;
    descripcion: string | null;
    requiereEvidencia: boolean;
    activo: boolean;
    createdAt: string;
    updatedAt: string | null;
}
