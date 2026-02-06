import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { CreateTipoVehiculoDTO, UpdateTipoVehiculoDTO } from "@/types/domain/tipo-vehiculo.types";
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from "@/lib/mappers/tipo-vehiculo.mapper";
import { Result, ok, err, NotFoundError, ConflictError } from "@/types/result.types";

export class TipoVehiculoService {
    async getAll(): Promise<Result<any[]>> { // Intentionally returning raw response mapped to avoid forcing strict response type on array yet
        try {
            const tipos = await prisma.tipoVehiculo.findMany({
                where: { activo: true },
                orderBy: { nombre: 'asc' }
            });
            return ok(tipos.map(mapEntityToResponse));
        } catch (error) {
            return err(error as Error);
        }
    }

    async getById(id: string): Promise<Result<any>> {
        try {
            const tipo = await prisma.tipoVehiculo.findUnique({
                where: { id }
            });

            if (!tipo) {
                return err(new NotFoundError("Tipo de Vehículo"));
            }

            return ok(mapEntityToResponse(tipo));
        } catch (error) {
            return err(error as Error);
        }
    }

    async create(data: CreateTipoVehiculoDTO): Promise<Result<any>> {
        try {
            // Check duplicados
            const existing = await prisma.tipoVehiculo.findUnique({
                where: { nombre: data.nombre }
            });

            if (existing) {
                return err(new ConflictError(`El tipo de vehículo '${data.nombre}' ya existe.`));
            }

            const input = mapDtoToPrismaCreate(data);
            const created = await prisma.tipoVehiculo.create({ data: input });
            return ok(mapEntityToResponse(created));
        } catch (error) {
            return err(error as Error);
        }
    }

    async update(id: string, data: UpdateTipoVehiculoDTO): Promise<Result<any>> {
        try {
            if (data.nombre) {
                const existing = await prisma.tipoVehiculo.findUnique({
                    where: { nombre: data.nombre }
                });
                if (existing && existing.id !== id) {
                    return err(new ConflictError(`El tipo de vehículo '${data.nombre}' ya existe.`));
                }
            }

            const input = mapDtoToPrismaUpdate(data);
            const updated = await prisma.tipoVehiculo.update({
                where: { id },
                data: input
            });
            return ok(mapEntityToResponse(updated));
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Tipo de Vehículo"));
            }
            return err(error as Error);
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            // Soft delete
            await prisma.tipoVehiculo.update({
                where: { id },
                data: { activo: false }
            });
            return ok(undefined);
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Tipo de Vehículo"));
            }
            return err(error as Error);
        }
    }
}

export const tipoVehiculoService = new TipoVehiculoService();
