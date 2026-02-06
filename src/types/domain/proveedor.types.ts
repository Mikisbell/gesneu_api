import { Prisma } from '@prisma/client';
import { ProveedorId } from '../branded.types';

export enum TipoProveedorEnum {
    FABRICANTE = 'FABRICANTE',
    DISTRIBUIDOR = 'DISTRIBUIDOR',
    SERVICIO_REPARACION = 'SERVICIO_REPARACION',
    SERVICIO_REENCAUCHE = 'SERVICIO_REENCAUCHE',
    OTRO = 'OTRO'
}

export interface ProveedorEntity extends Prisma.ProveedorGetPayload<{}> { }

export interface CreateProveedorDTO {
    nombre: string;
    ruc?: string;
    tipo: TipoProveedorEnum | string;
    direccion?: string;
    telefono?: string;
    email?: string;
    contacto_principal?: string;
    activo?: boolean;
}

export interface UpdateProveedorDTO extends Partial<CreateProveedorDTO> { }

export interface ProveedorResponse {
    id: ProveedorId;
    nombre: string;
    ruc: string | null;
    tipo: string;
    direccion: string | null;
    telefono: string | null;
    email: string | null;
    contacto: string | null; // contacto_nombre
    activo: boolean;
    createdAt: string;
    updatedAt: string;
}
