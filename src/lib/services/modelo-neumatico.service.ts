
import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { CreateModeloNeumaticoDTO, UpdateModeloNeumaticoDTO, ModeloNeumaticoResponse } from "@/types/domain/modelo-neumatico.types";
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from "@/lib/mappers/modelo-neumatico.mapper";
import { Result, ok, err, NotFoundError, ConflictError } from "@/types/result.types";

export class ModeloNeumaticoService {
    async getAll(includeInactive = false): Promise<Result<ModeloNeumaticoResponse[]>> {
        try {
            const where: Prisma.ModeloNeumaticoWhereInput = includeInactive ? {} : { activo: true };
            const modelos = await prisma.modeloNeumatico.findMany({
                where,
                include: { fabricante: true },
                orderBy: { nombre_modelo: 'asc' }
            });
            return ok(modelos.map(mapEntityToResponse));
        } catch (error) {
            return err(error as Error);
        }
    }

    async getById(id: string): Promise<Result<ModeloNeumaticoResponse>> {
        try {
            const modelo = await prisma.modeloNeumatico.findUnique({
                where: { id },
                include: { fabricante: true }
            });

            if (!modelo) {
                return err(new NotFoundError("Modelo de Neumático"));
            }

            return ok(mapEntityToResponse(modelo));
        } catch (error) {
            return err(error as Error);
        }
    }

    async create(data: CreateModeloNeumaticoDTO): Promise<Result<ModeloNeumaticoResponse>> {
        try {
            // Check Unique Constraint [fabricante_id, nombre_modelo, medida]
            const existing = await prisma.modeloNeumatico.findUnique({
                where: {
                    fabricante_id_nombre_modelo_medida: {
                        fabricante_id: data.fabricante_id,
                        nombre_modelo: data.nombre,
                        medida: data.medida
                    }
                }
            });

            if (existing) {
                return err(new ConflictError(`El modelo '${data.nombre}' con medida '${data.medida}' ya existe para este fabricante.`));
            }

            const input = mapDtoToPrismaCreate(data);
            const created = await prisma.modeloNeumatico.create({
                data: input,
                include: { fabricante: true }
            });
            return ok(mapEntityToResponse(created));
        } catch (error) {
            return err(error as Error);
        }
    }

    async update(id: string, data: UpdateModeloNeumaticoDTO): Promise<Result<ModeloNeumaticoResponse>> {
        try {
            // If relevant fields changed, check uniqueness logic (complex, skipping for simplicity unless Name/Fabricante changed)
            // Prisma throws P2002 if unique constraint violated, handled below.

            const input = mapDtoToPrismaUpdate(data);
            const updated = await prisma.modeloNeumatico.update({
                where: { id },
                data: input,
                include: { fabricante: true }
            });
            return ok(mapEntityToResponse(updated));
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError) {
                if (error.code === 'P2025') return err(new NotFoundError("Modelo de Neumático"));
                if (error.code === 'P2002') return err(new ConflictError("Combinación Fabricante/Modelo/Medida ya existe."));
            }
            return err(error as Error);
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            await prisma.modeloNeumatico.update({
                where: { id },
                data: { activo: false }
            });
            return ok(undefined);
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Modelo de Neumático"));
            }
            return err(error as Error);
        }
    }
}

export const modeloNeumaticoService = new ModeloNeumaticoService();
