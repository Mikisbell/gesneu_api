import { Prisma } from '@prisma/client';
import { CreateModeloNeumaticoDTO, UpdateModeloNeumaticoDTO, ModeloNeumaticoEntity, ModeloNeumaticoResponse } from '@/types/domain/modelo-neumatico.types';

export function mapDtoToPrismaCreate(dto: CreateModeloNeumaticoDTO): Prisma.ModeloNeumaticoCreateInput {
    return {
        fabricante: { connect: { id: dto.fabricante_id } },
        nombre_modelo: dto.nombre,
        medida: dto.medida,
        profundidad_original_mm: dto.profundidad_original_mm,
        profundidad_minima_retiro_mm: dto.profundidad_minima_retiro_mm ?? 3.0,
        presion_recomendada_psi: dto.presion_recomendada_psi,
        patron_dibujo: dto.patron_dibujo,
        tipo_servicio: dto.tipo_servicio,
        indice_carga: dto.indice_carga,
        indice_velocidad: dto.indice_velocidad,
        permite_reencauche: dto.permite_reencauche ?? false,
        reencauches_maximos: dto.reencauches_maximos ?? 0,
        activo: true,
    };
}

export function mapDtoToPrismaUpdate(dto: UpdateModeloNeumaticoDTO): Prisma.ModeloNeumaticoUpdateInput {
    const input: Prisma.ModeloNeumaticoUpdateInput = {};
    if (dto.fabricante_id !== undefined) input.fabricante = { connect: { id: dto.fabricante_id } };
    if (dto.nombre !== undefined) input.nombre_modelo = dto.nombre;
    if (dto.medida !== undefined) input.medida = dto.medida;
    if (dto.profundidad_original_mm !== undefined) input.profundidad_original_mm = dto.profundidad_original_mm;
    if (dto.profundidad_minima_retiro_mm !== undefined) input.profundidad_minima_retiro_mm = dto.profundidad_minima_retiro_mm;
    if (dto.presion_recomendada_psi !== undefined) input.presion_recomendada_psi = dto.presion_recomendada_psi;
    if (dto.patron_dibujo !== undefined) input.patron_dibujo = dto.patron_dibujo;
    if (dto.tipo_servicio !== undefined) input.tipo_servicio = dto.tipo_servicio;
    if (dto.indice_carga !== undefined) input.indice_carga = dto.indice_carga;
    if (dto.indice_velocidad !== undefined) input.indice_velocidad = dto.indice_velocidad;
    if (dto.permite_reencauche !== undefined) input.permite_reencauche = dto.permite_reencauche;
    if (dto.reencauches_maximos !== undefined) input.reencauches_maximos = dto.reencauches_maximos;
    if (dto.activo !== undefined) input.activo = dto.activo;
    return input;
}

export function mapEntityToResponse(entity: ModeloNeumaticoEntity): ModeloNeumaticoResponse {
    return {
        id: entity.id,
        fabricante: {
            id: entity.fabricante.id,
            nombre: entity.fabricante.nombre,
        },
        nombre: entity.nombre_modelo,
        medida: entity.medida,
        profundidadOriginal: Number(entity.profundidad_original_mm),
        profundidadMinimaRetiro: entity.profundidad_minima_retiro_mm ? Number(entity.profundidad_minima_retiro_mm) : 3.0,
        presionRecomendada: entity.presion_recomendada_psi ? Number(entity.presion_recomendada_psi) : null,
        patronDibujo: entity.patron_dibujo,
        tipoServicio: entity.tipo_servicio,
        especificaciones: {
            indiceCarga: entity.indice_carga,
            indiceVelocidad: entity.indice_velocidad,
        },
        reencauche: {
            permitido: entity.permite_reencauche,
            maximos: entity.reencauches_maximos,
        },
        activo: entity.activo,
        createdAt: entity.creado_en.toISOString(),
        updatedAt: entity.actualizado_en?.toISOString() ?? null,
    };
}
