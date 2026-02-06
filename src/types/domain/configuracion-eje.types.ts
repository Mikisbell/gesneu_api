
import { ConfiguracionEje, PosicionNeumatico, TipoEjeEnum } from '@prisma/client';
import { PosicionNeumaticoResponse } from './posicion-neumatico.types';

export type ConfiguracionEjeEntity = ConfiguracionEje & {
    posiciones?: PosicionNeumatico[];
};

export interface CreateConfiguracionEjeDTO {
    tipo_vehiculo_id: string;
    numero_eje: number;
    nombre_eje: string;
    tipo_eje: TipoEjeEnum;
    numero_posiciones: number;
    posiciones_duales: boolean;
    permite_reencauchados?: boolean;
    neumaticos_por_posicion?: number;
}

export interface UpdateConfiguracionEjeDTO extends Partial<CreateConfiguracionEjeDTO> { }

export interface ConfiguracionEjeResponse {
    id: string;
    tipoVehiculoId: string;
    numeroEje: number;
    nombreEje: string;
    tipoEje: TipoEjeEnum;
    numeroPosiciones: number;
    posicionesDuales: boolean;
    permiteReencauchados: boolean;
    neumaticosPorPosicion: number;
    posiciones?: PosicionNeumaticoResponse[];
    createdAt: string;
    updatedAt: string | null;
}
