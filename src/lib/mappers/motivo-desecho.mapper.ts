
import { Prisma } from '@prisma/client';
import { CreateMotivoDesechoDTO, UpdateMotivoDesechoDTO, MotivoDesechoEntity, MotivoDesechoResponse } from '@/types/domain/motivo-desecho.types';

export function mapDtoToPrismaCreate(dto: CreateMotivoDesechoDTO): Prisma.MotivoDesechoCreateInput {
    return {
        codigo: dto.codigo,
        nombre: dto.nombre,
        descripcion: dto.descripcion,
        requiere_evidencia: dto.requiere_evidencia ?? false,
        activo: true,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateMotivoDesechoDTO): Prisma.MotivoDesechoUpdateInput {
    const input: Prisma.MotivoDesechoUpdateInput = {};
    if (dto.codigo !== undefined) input.codigo = dto.codigo;
    if (dto.nombre !== undefined) input.nombre = dto.nombre;
    if (dto.descripcion !== undefined) input.descripcion = dto.descripcion;
    if (dto.requiere_evidencia !== undefined) input.requiere_evidencia = dto.requiere_evidencia;
    if (dto.activo !== undefined) input.activo = dto.activo;
    return input;
}

export function mapEntityToResponse(entity: MotivoDesechoEntity): MotivoDesechoResponse {
    return {
        id: entity.id,
        codigo: entity.codigo,
        nombre: entity.nombre,
        descripcion: entity.descripcion,
        requiereEvidencia: entity.requiere_evidencia,
        activo: entity.activo,
        createdAt: entity.creado_en.toISOString(),
        updatedAt: entity.actualizado_en?.toISOString() ?? null,
    };
}
