
import { Prisma } from '@prisma/client';
import { CreateFabricanteDTO, UpdateFabricanteDTO, FabricanteEntity, FabricanteResponse } from '@/types/domain/fabricante.types';

export function mapDtoToPrismaCreate(dto: CreateFabricanteDTO): Prisma.FabricanteNeumaticoCreateInput {
    return {
        nombre: dto.nombre,
        codigo_abreviado: dto.codigoAbreviado,
        pais_origen: dto.paisOrigen,
        sitio_web: dto.sitioWeb,
        activo: true,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateFabricanteDTO): Prisma.FabricanteNeumaticoUpdateInput {
    const input: Prisma.FabricanteNeumaticoUpdateInput = {};
    if (dto.nombre !== undefined) input.nombre = dto.nombre;
    if (dto.codigoAbreviado !== undefined) input.codigo_abreviado = dto.codigoAbreviado;
    if (dto.paisOrigen !== undefined) input.pais_origen = dto.paisOrigen;
    if (dto.sitioWeb !== undefined) input.sitio_web = dto.sitioWeb;
    if (dto.activo !== undefined) input.activo = dto.activo;
    return input;
}

export function mapEntityToResponse(entity: FabricanteEntity): FabricanteResponse {
    return {
        id: entity.id,
        nombre: entity.nombre,
        codigoAbreviado: entity.codigo_abreviado,
        paisOrigen: entity.pais_origen,
        sitioWeb: entity.sitio_web,
        activo: entity.activo,
        createdAt: entity.creado_en.toISOString(),
        updatedAt: entity.actualizado_en?.toISOString() ?? null,
    };
}
