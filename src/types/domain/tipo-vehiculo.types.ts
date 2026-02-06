
import { TipoVehiculo } from '@prisma/client';

export type TipoVehiculoEntity = TipoVehiculo;

export interface CreateTipoVehiculoDTO {
    nombre: string;
    descripcion?: string;
    activo?: boolean;
}

export interface UpdateTipoVehiculoDTO extends Partial<CreateTipoVehiculoDTO> { }

export interface TipoVehiculoResponse {
    id: string;
    nombre: string;
    descripcion: string | null;
    activo: boolean;
}
