
import { PosicionNeumatico, LadoVehiculoEnum } from '@prisma/client';

export type PosicionNeumaticoEntity = PosicionNeumatico;

export interface PosicionNeumaticoResponse {
    id: string;
    configuracionEjeId: string;
    codigo: string;
    etiqueta: string | null;
    lado: LadoVehiculoEnum;
    posicionRelativa: number;
    esInterna: boolean;
    esDireccion: boolean;
    esTraccion: boolean;
    requiereNeumaticoEspecifico: boolean;
    permiteReencauchado: boolean;
    createdAt: string;
    updatedAt: string | null;
}

export interface UpdatePosicionNeumaticoDTO {
    permiteReencauchado?: boolean;
    requiereNeumaticoEspecifico?: boolean;
}
