
import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { CreateFabricanteDTO, UpdateFabricanteDTO, FabricanteResponse } from "@/types/domain/fabricante.types";
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from "@/lib/mappers/fabricante.mapper";
import { Result, ok, err, NotFoundError, ConflictError } from "@/types/result.types";

export class FabricanteService {
    async getAll(includeInactive = false): Promise<Result<FabricanteResponse[]>> {
        try {
            const where: Prisma.FabricanteNeumaticoWhereInput = includeInactive ? {} : { activo: true };
            const fabricantes = await prisma.fabricanteNeumatico.findMany({
                where,
                orderBy: { nombre: 'asc' }
            });
            return ok(fabricantes.map(mapEntityToResponse));
        } catch (error) {
            return err(error as Error);
        }
    }

    async getById(id: string): Promise<Result<FabricanteResponse>> {
        try {
            const fabricante = await prisma.fabricanteNeumatico.findUnique({
                where: { id }
            });

            if (!fabricante) {
                return err(new NotFoundError("Fabricante"));
            }

            return ok(mapEntityToResponse(fabricante));
        } catch (error) {
            return err(error as Error);
        }
    }

    async create(data: CreateFabricanteDTO): Promise<Result<FabricanteResponse>> {
        try {
            // Validate Name duplicates?
            const existing = await prisma.fabricanteNeumatico.findFirst({
                where: { nombre: { equals: data.nombre, mode: 'insensitive' } } // loose check
            });
            // Also check codigo_abreviado unique constraint
            if (data.codigoAbreviado) {
                const existingCode = await prisma.fabricanteNeumatico.findUnique({
                    where: { codigo_abreviado: data.codigoAbreviado }
                });
                if (existingCode) return err(new ConflictError(`El código '${data.codigoAbreviado}' ya existe.`));
            }

            const input = mapDtoToPrismaCreate(data);
            const created = await prisma.fabricanteNeumatico.create({ data: input });
            return ok(mapEntityToResponse(created));
        } catch (error) {
            return err(error as Error);
        }
    }

    async update(id: string, data: UpdateFabricanteDTO): Promise<Result<FabricanteResponse>> {
        try {
            if (data.codigoAbreviado) {
                const existingCode = await prisma.fabricanteNeumatico.findUnique({
                    where: { codigo_abreviado: data.codigoAbreviado }
                });
                if (existingCode && existingCode.id !== id) return err(new ConflictError(`El código '${data.codigoAbreviado}' ya existe.`));
            }

            const input = mapDtoToPrismaUpdate(data);
            const updated = await prisma.fabricanteNeumatico.update({
                where: { id },
                data: input
            });
            return ok(mapEntityToResponse(updated));
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Fabricante"));
            }
            return err(error as Error);
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            await prisma.fabricanteNeumatico.update({
                where: { id },
                data: { activo: false }
            });
            return ok(undefined);
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Fabricante"));
            }
            return err(error as Error);
        }
    }
}

export const fabricanteService = new FabricanteService();
