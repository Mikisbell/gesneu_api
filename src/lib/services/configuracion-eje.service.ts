
import { prisma } from "@/lib/prisma";
import { Prisma, TipoEjeEnum, LadoVehiculoEnum } from "@prisma/client";
import { CreateConfiguracionEjeDTO, UpdateConfiguracionEjeDTO, ConfiguracionEjeResponse } from "@/types/domain/configuracion-eje.types";
import { mapDtoToPrismaCreate, mapDtoToPrismaUpdate, mapEntityToResponse } from "@/lib/mappers/configuracion-eje.mapper";
import { Result, ok, err, NotFoundError, ConflictError } from "@/types/result.types";

export class ConfiguracionEjeService {

    async getByTipoVehiculo(tipoVehiculoId: string): Promise<Result<ConfiguracionEjeResponse[]>> {
        try {
            const configs = await prisma.configuracionEje.findMany({
                where: { tipo_vehiculo_id: tipoVehiculoId },
                orderBy: { numero_eje: 'asc' },
                include: { posiciones: { orderBy: { codigo_posicion: 'asc' } } }
            });
            return ok(configs.map(mapEntityToResponse));
        } catch (error) {
            return err(error as Error);
        }
    }

    async create(data: CreateConfiguracionEjeDTO): Promise<Result<ConfiguracionEjeResponse>> {
        try {
            // Validate Uniqueness: Eje number within TipoVehiculo
            const existing = await prisma.configuracionEje.findUnique({
                where: {
                    tipo_vehiculo_id_numero_eje: {
                        tipo_vehiculo_id: data.tipo_vehiculo_id,
                        numero_eje: data.numero_eje
                    }
                }
            });

            if (existing) {
                return err(new ConflictError(`El eje número ${data.numero_eje} ya existe para este tipo de vehículo.`));
            }

            // Transaction: Create Config + Generate Positions
            const result = await prisma.$transaction(async (tx) => {
                const input = mapDtoToPrismaCreate(data);
                const config = await tx.configuracionEje.create({ data: input });

                // Generate Positions Logic
                const posicionesData = this.generatePosiciones(config);

                if (posicionesData.length > 0) {
                    await tx.posicionNeumatico.createMany({
                        data: posicionesData
                    });
                }

                return await tx.configuracionEje.findUniqueOrThrow({
                    where: { id: config.id },
                    include: { posiciones: { orderBy: { codigo_posicion: 'asc' } } }
                });
            });

            return ok(mapEntityToResponse(result));
        } catch (error) {
            return err(error as Error);
        }
    }

    async delete(id: string): Promise<Result<void>> {
        try {
            // Cascade delete is usually handled by DB, but safe to verify or delete explicit
            // Standard: Delete Config -> Deletes Positions (check schema or logic).
            // Schema has NO explicit cascade on Relation? 
            // `configuracion_eje ConfiguracionEje @relation(fields: [configuracion_eje_id], references: [id])`
            // If No Action, we must delete positions first.
            // I'll delete positions first to be safe within transaction.

            await prisma.$transaction(async (tx) => {
                await tx.posicionNeumatico.deleteMany({
                    where: { configuracion_eje_id: id }
                });
                await tx.configuracionEje.delete({
                    where: { id }
                });
            });

            return ok(undefined);
        } catch (error) {
            if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
                return err(new NotFoundError("Configuración de Eje"));
            }
            return err(error as Error);
        }
    }

    // --- Helper: Position Generator ---
    private generatePosiciones(config: {
        id: string;
        numero_eje: number;
        tipo_eje: TipoEjeEnum;
        posiciones_duales: boolean;
        permite_reencauchados: boolean
    }): Prisma.PosicionNeumaticoCreateManyInput[] {
        const positions: Prisma.PosicionNeumaticoCreateManyInput[] = [];
        const eje = config.numero_eje;
        const isDual = config.posiciones_duales;
        const tipo = config.tipo_eje;

        const common = {
            configuracion_eje_id: config.id,
            es_direccion: tipo === TipoEjeEnum.DIRECCION,
            es_traccion: tipo === TipoEjeEnum.TRACCION,
            permite_reencauchado: config.permite_reencauchados, // Default inherit
            requiere_neumatico_especifico: false
        };

        if (!isDual) {
            // Simple Axle: 1I, 1D
            positions.push({
                ...common,
                codigo_posicion: `${eje}I`, // Ex: 1I
                etiqueta_posicion: `Eje ${eje} Izquierdo`,
                lado: LadoVehiculoEnum.IZQUIERDO,
                posicion_relativa: 1,
                es_interna: false
            });
            positions.push({
                ...common,
                codigo_posicion: `${eje}D`, // Ex: 1D
                etiqueta_posicion: `Eje ${eje} Derecho`,
                lado: LadoVehiculoEnum.DERECHO,
                posicion_relativa: 2,
                es_interna: false
            });
        } else {
            // Dual Axle: 2II, 2IE, 2DI, 2DE
            // Order: Left-Outer, Left-Inner, Right-Inner, Right-Outer?
            // Usually visual representation L->R.

            // Left Outer (IE) - Izquierda Externa
            positions.push({
                ...common,
                codigo_posicion: `${eje}IE`,
                etiqueta_posicion: `Eje ${eje} Izquierdo Externo`,
                lado: LadoVehiculoEnum.IZQUIERDO,
                posicion_relativa: 1,
                es_interna: false // External
            });
            // Left Inner (II) - Izquierda Interna
            positions.push({
                ...common,
                codigo_posicion: `${eje}II`,
                etiqueta_posicion: `Eje ${eje} Izquierdo Interno`,
                lado: LadoVehiculoEnum.IZQUIERDO,
                posicion_relativa: 2,
                es_interna: true
            });
            // Right Inner (DI) - Derecha Interna
            positions.push({
                ...common,
                codigo_posicion: `${eje}DI`,
                etiqueta_posicion: `Eje ${eje} Derecho Interno`,
                lado: LadoVehiculoEnum.DERECHO,
                posicion_relativa: 3,
                es_interna: true
            });
            // Right Outer (DE) - Derecha Externa
            positions.push({
                ...common,
                codigo_posicion: `${eje}DE`,
                etiqueta_posicion: `Eje ${eje} Derecho Externo`,
                lado: LadoVehiculoEnum.DERECHO,
                posicion_relativa: 4,
                es_interna: false
            });
        }

        return positions;
    }
}

export const configuracionEjeService = new ConfiguracionEjeService();
