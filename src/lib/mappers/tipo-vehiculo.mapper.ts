
import { Prisma } from '@prisma/client';
import { CreateTipoVehiculoDTO, UpdateTipoVehiculoDTO, TipoVehiculoEntity, TipoVehiculoResponse } from '@/types/domain/tipo-vehiculo.types';

export function mapDtoToPrismaCreate(dto: CreateTipoVehiculoDTO): Prisma.TipoVehiculoCreateInput {
    return {
        nombre: dto.nombre,
        descripcion: dto.descripcion,
        activo: dto.activo ?? true,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateTipoVehiculoDTO): Prisma.TipoVehiculoUpdateInput {
    return {
        nombre: dto.nombre,
        descripcion: dto.descripcion,
        activo: dto.activo,
    };
}

export function mapEntityToResponse(entity: TipoVehiculoEntity): TipoVehiculoResponse {
    return {
        id: entity.id,
        nombre: entity.nombre,
        descripcion: entity.descripcion,
        activo: entity.activo,
    };
}
