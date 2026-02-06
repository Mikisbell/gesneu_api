import { Prisma } from '@prisma/client';
import { CreateProveedorDTO, ProveedorEntity, ProveedorResponse, UpdateProveedorDTO } from '@/types/domain/proveedor.types';
import { asProveedorId } from '@/types/branded.types';

export function mapDtoToPrismaCreate(dto: CreateProveedorDTO): Omit<Prisma.ProveedorCreateInput, 'empresa'> {
    return {
        nombre: dto.nombre,
        ruc: dto.ruc || null,
        tipo: dto.tipo as any, // Enum
        direccion: dto.direccion || null,
        telefono: dto.telefono || null,
        email: dto.email || null,
        contacto_principal: dto.contacto_principal || null,
        activo: dto.activo ?? true,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateProveedorDTO): Prisma.ProveedorUpdateInput {
    // Manually map fields to avoid undefined overwrites
    const data: Prisma.ProveedorUpdateInput = {};
    if (dto.nombre) data.nombre = dto.nombre;
    if (dto.ruc !== undefined) data.ruc = dto.ruc;
    if (dto.tipo) data.tipo = dto.tipo as any;
    if (dto.direccion !== undefined) data.direccion = dto.direccion;
    if (dto.telefono !== undefined) data.telefono = dto.telefono;
    if (dto.email !== undefined) data.email = dto.email;
    if (dto.contacto_principal !== undefined) data.contacto_principal = dto.contacto_principal;
    if (dto.activo !== undefined) data.activo = dto.activo;
    return data;
}

export function mapEntityToResponse(entity: ProveedorEntity): ProveedorResponse {
    const e = entity as any;
    return {
        id: asProveedorId(e.id),
        nombre: e.nombre,
        ruc: e.ruc,
        tipo: e.tipo,
        direccion: e.direccion,
        telefono: e.telefono,
        email: e.email,
        contacto: e.contacto_principal, // Mapped to 'contacto' in Response
        activo: e.activo,
        createdAt: e.creado_en?.toISOString() ?? new Date().toISOString(),
        updatedAt: e.actualizado_en?.toISOString() ?? new Date().toISOString(),
    };
}
