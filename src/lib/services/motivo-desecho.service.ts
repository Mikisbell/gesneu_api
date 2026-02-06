
import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { CreateMotivoDesechoDTO, UpdateMotivoDesechoDTO, MotivoDesechoResponse } from "@/types/domain/motivo-desecho.types";
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from "@/lib/mappers/motivo-desecho.mapper";
import { Result, ok, err, NotFoundError, ConflictError } from "@/types/result.types";

export class MotivoDesechoService {
    async getAll(includeInactive = false): Promise<Result<MotivoDesechoResponse[]>> {
        try {
            const where: Prisma.MotivoDesechoWhereInput = includeInactive ? {} : { activo: true };
            const motivos = await prisma.motivoDesecho.findMany({
                where,
                orderBy: { codigo: 'asc' }
            });
            return ok(motivos.map(mapEntityToResponse));
        } catch (error) {
            return err(error as Error);
        }
    }

    async getById(id: string): Promise<Result<MotivoDesechoResponse>> {
        try {
            const motivo = await prisma.motivoDesecho.findUnique({
                where: { id }
            });

            if (!motivo) {
                return err(new NotFoundError("Motivo de Desecho"));
            }

            return ok(mapEntityToResponse(motivo));
        } catch (error) {
            return err(error as Error);
        }
    }

    async create(data: CreateMotivoDesechoDTO): Promise<Result<MotivoDesechoResponse>> {
        try {
            const existing = await prisma.motivoDesecho.findUnique({
                where: { codigo: data.codigo }
            });

            if (existing) {
                return err(new ConflictError(`El código de desecho '${data.codigo}' ya existe.`));
            }

            const input = mapDtoToPrismaCreate(data);
            const created = await prisma.motivoDesecho.create({ data: input });
            return ok(mapEntityToResponse(created));
        } catch (error) {
            return err(error as Error);
        }
    }

    async update(id: string, data: UpdateMotivoDesechoDTO): Promise<Result<MotivoDesechoResponse>> {
        try {
            if (data.codigo) {
                const existing = await prisma.motivoDesecho.findUnique({
                    where: { codigo: data.codigo }
                });
                if (existing && existing.id !== id) {
                    return err(new ConflictError(`El código de desecho '${data.codigo}' ya existe.`));
                }
            }

            const input = mapDtoToPrismaUpdate(data);
            const updated = await prisma.motivoDesecho.update({
                where: { id },
                data: input
            });
            return ok(mapEntityToResponse(updated));
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Motivo de Desecho"));
            }
            return err(error as Error);
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            await prisma.motivoDesecho.update({
                where: { id },
                data: { activo: false }
            });
            return ok(undefined);
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Motivo de Desecho"));
            }
            return err(error as Error);
        }
    }
}

export const motivoDesechoService = new MotivoDesechoService();
