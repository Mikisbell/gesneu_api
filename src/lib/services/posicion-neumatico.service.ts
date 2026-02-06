
import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { UpdatePosicionNeumaticoDTO, PosicionNeumaticoResponse } from "@/types/domain/posicion-neumatico.types";
import { mapPosicionEntityToResponse } from "@/lib/mappers/posicion-neumatico.mapper";
import { Result, ok, err, NotFoundError } from "@/types/result.types";

export class PosicionNeumaticoService {

    // Usually positions are accessed via Config or Vehicle. 
    // But modifying specific rules for a position (override):

    async update(id: string, data: UpdatePosicionNeumaticoDTO): Promise<Result<PosicionNeumaticoResponse>> {
        try {
            const input: Prisma.PosicionNeumaticoUpdateInput = {};
            if (data.permiteReencauchado !== undefined) input.permite_reencauchado = data.permiteReencauchado;
            if (data.requiereNeumaticoEspecifico !== undefined) input.requiere_neumatico_especifico = data.requiereNeumaticoEspecifico;

            const updated = await prisma.posicionNeumatico.update({
                where: { id },
                data: input
            });
            return ok(mapPosicionEntityToResponse(updated));
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Posición de Neumático"));
            }
            return err(error as Error);
        }
    }
}

export const posicionNeumaticoService = new PosicionNeumaticoService();
