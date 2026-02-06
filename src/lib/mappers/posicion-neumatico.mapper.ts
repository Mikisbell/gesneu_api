
import { PosicionNeumaticoEntity, PosicionNeumaticoResponse } from '@/types/domain/posicion-neumatico.types';

export function mapPosicionEntityToResponse(entity: PosicionNeumaticoEntity): PosicionNeumaticoResponse {
    return {
        id: entity.id,
        configuracionEjeId: entity.configuracion_eje_id,
        codigo: entity.codigo_posicion,
        etiqueta: entity.etiqueta_posicion,
        lado: entity.lado,
        posicionRelativa: entity.posicion_relativa,
        esInterna: entity.es_interna,
        esDireccion: entity.es_direccion,
        esTraccion: entity.es_traccion,
        requiereNeumaticoEspecifico: entity.requiere_neumatico_especifico,
        permiteReencauchado: entity.permite_reencauchado,
        createdAt: entity.creado_en.toISOString(),
        updatedAt: entity.actualizado_en?.toISOString() ?? null,
    };
}
