/**
 * Almacen Mappers
 */
import { Prisma } from '@prisma/client';
import { AlmacenEntity, AlmacenResponse, CreateAlmacenDTO, UpdateAlmacenDTO } from '@/types/domain/almacen.types';
import { asAlmacenId } from '@/types/branded.types';

export function mapDtoToPrismaCreate(dto: CreateAlmacenDTO): Prisma.AlmacenCreateInput {
    return {
        codigo: dto.codigo,
        nombre: dto.nombre,
        // descripcion: dto.descripcion, // Not in schema
        direccion: dto.ubicacion, // Mapping 'ubicacion' DTO to 'direccion' DB
        activo: dto.activo ?? true,
        // empresa connection handling in service
        empresa: { connect: { id: 'temp' } } // Placeholder, logic in service
    };
}

// AlmacenUpdateInput requires slightly different structure or direct scalars
export function mapDtoToPrismaUpdate(dto: UpdateAlmacenDTO): Prisma.AlmacenUpdateInput {
    const data: Prisma.AlmacenUpdateInput = {};
    if (dto.codigo) data.codigo = dto.codigo;
    if (dto.nombre) data.nombre = dto.nombre;
    // if (dto.descripcion !== undefined) data.descripcion = dto.descripcion;
    if (dto.ubicacion !== undefined) data.direccion = dto.ubicacion;
    if (dto.activo !== undefined) data.activo = dto.activo;
    return data;
}

export function mapEntityToResponse(entity: AlmacenEntity): AlmacenResponse {
    const e = entity as any; // Safe cast for DB specific fields
    return {
        id: asAlmacenId(e.id),
        codigo: e.codigo,
        nombre: e.nombre,
        descripcion: null, // Field not in DB
        ubicacion: e.direccion, // DB field is 'direccion'
        activo: e.activo,
        createdAt: e.creado_en?.toISOString() ?? new Date().toISOString(),
        updatedAt: e.actualizado_en?.toISOString() ?? new Date().toISOString(),
    } satisfies AlmacenResponse;
}
