
import { Prisma } from '@prisma/client';
import { CreateConfiguracionEjeDTO, UpdateConfiguracionEjeDTO, ConfiguracionEjeEntity, ConfiguracionEjeResponse } from '@/types/domain/configuracion-eje.types';
import { mapPosicionEntityToResponse } from './posicion-neumatico.mapper';

export function mapDtoToPrismaCreate(dto: CreateConfiguracionEjeDTO): Prisma.ConfiguracionEjeCreateInput {
    return {
        tipo_vehiculo: { connect: { id: dto.tipo_vehiculo_id } },
        numero_eje: dto.numero_eje,
        nombre_eje: dto.nombre_eje,
        tipo_eje: dto.tipo_eje,
        numero_posiciones: dto.numero_posiciones,
        posiciones_duales: dto.posiciones_duales,
        permite_reencauchados: dto.permite_reencauchados ?? true,
        neumaticos_por_posicion: dto.neumaticos_por_posicion ?? 1,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateConfiguracionEjeDTO): Prisma.ConfiguracionEjeUpdateInput {
    const input: Prisma.ConfiguracionEjeUpdateInput = {};
    if (dto.numero_eje !== undefined) input.numero_eje = dto.numero_eje;
    if (dto.nombre_eje !== undefined) input.nombre_eje = dto.nombre_eje;
    if (dto.tipo_eje !== undefined) input.tipo_eje = dto.tipo_eje;
    if (dto.numero_posiciones !== undefined) input.numero_posiciones = dto.numero_posiciones;
    if (dto.posiciones_duales !== undefined) input.posiciones_duales = dto.posiciones_duales;
    if (dto.permite_reencauchados !== undefined) input.permite_reencauchados = dto.permite_reencauchados;
    return input;
}

export function mapEntityToResponse(entity: ConfiguracionEjeEntity): ConfiguracionEjeResponse {
    return {
        id: entity.id,
        tipoVehiculoId: entity.tipo_vehiculo_id,
        numeroEje: entity.numero_eje,
        nombreEje: entity.nombre_eje,
        tipoEje: entity.tipo_eje,
        numeroPosiciones: entity.numero_posiciones,
        posicionesDuales: entity.posiciones_duales,
        permiteReencauchados: entity.permite_reencauchados,
        neumaticosPorPosicion: entity.neumaticos_por_posicion,
        posiciones: entity.posiciones?.map(mapPosicionEntityToResponse),
        createdAt: entity.creado_en.toISOString(),
        updatedAt: entity.actualizado_en?.toISOString() ?? null,
    };
}
