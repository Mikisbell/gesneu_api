import { Prisma } from '@prisma/client';
import { AlmacenEntity, AlmacenResponse, CreateAlmacenDTO, UpdateAlmacenDTO } from '@/types/domain/almacen.types';
import { asAlmacenId } from '@/types/branded.types';

export function mapDtoToPrismaCreate(dto: CreateAlmacenDTO): Omit<Prisma.AlmacenCreateInput, 'empresa'> {
    return {
        codigo: dto.codigo,
        nombre: dto.nombre,
        tipo: dto.tipo,
        direccion: dto.direccion,
        activo: dto.activo ?? true,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateAlmacenDTO): Prisma.AlmacenUpdateInput {
    const data: Prisma.AlmacenUpdateInput = {};
    if (dto.codigo) data.codigo = dto.codigo;
    if (dto.nombre) data.nombre = dto.nombre;
    if (dto.tipo) data.tipo = dto.tipo;
    if (dto.direccion !== undefined) data.direccion = dto.direccion;
    if (dto.activo !== undefined) data.activo = dto.activo;
    return data;
}

export function mapEntityToResponse(entity: AlmacenEntity): AlmacenResponse {
    const e = entity as any;
    return {
        id: asAlmacenId(e.id),
        codigo: e.codigo,
        nombre: e.nombre,
        tipo: e.tipo || null,
        direccion: e.direccion || null,
        activo: e.activo,
        createdAt: e.creado_en?.toISOString() ?? new Date().toISOString(),
        updatedAt: e.actualizado_en?.toISOString() ?? new Date().toISOString(),
    } satisfies AlmacenResponse;
}
