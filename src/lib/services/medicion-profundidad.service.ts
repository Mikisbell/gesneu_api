import { prisma } from '@/lib/prisma';
import { Prisma } from '@prisma/client';
import { CreateMedicionProfundidadSchema, CreateMedicionProfundidadDTO } from '@/lib/validators/medicion-profundidad.validator';
import { BusinessError } from '@/types/result.types';

export interface MedicionProfundidadResult {
    id: string;
    neumatico_id: string;
    evento_id: string | null;
    fecha_medicion: Date;
    profundidad_int: number;
    profundidad_cen: number;
    profundidad_ext: number;
    profundidad_prom: number;
    desgaste_irregular: boolean;
    tipo_desgaste: string | null;
    observaciones: string | null;
    kilometraje: number | null;
    creado_por: string | null;
    creado_en: Date;
}

export interface MedicionHistorialItem {
    id: string;
    fecha_medicion: Date;
    profundidad_int: number;
    profundidad_cen: number;
    profundidad_ext: number;
    profundidad_prom: number;
    desgaste_irregular: boolean;
    tipo_desgaste: string | null;
    observaciones: string | null;
    kilometraje: number | null;
    creado_por: string | null;
}

export class MedicionProfundidadService {
    /**
     * Validate that a neumatico belongs to the given empresa
     */
    async validateNeumaticoOwnership(neumaticoId: string, empresa_id: string): Promise<boolean> {
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId },
            select: { empresa_id: true }
        });

        return neumatico !== null && neumatico.empresa_id === empresa_id;
    }

    /**
     * Create a new depth measurement record
     */
    async create(
        data: CreateMedicionProfundidadDTO,
        usuarioId: string,
        empresa_id: string
    ): Promise<MedicionProfundidadResult> {
        const validated = CreateMedicionProfundidadSchema.parse(data);

        // Verify the neumatico belongs to the empresa
        const ownsNeumatico = await this.validateNeumaticoOwnership(
            validated.neumatico_id,
            empresa_id
        );

        if (!ownsNeumatico) {
            throw new BusinessError(
                'El neumatico no pertenece a la empresa',
                'FORBIDDEN',
                403
            );
        }

        const { profundidad_int, profundidad_cen, profundidad_ext } = validated;

        // Calculate average
        const profundidadProm = (profundidad_int + profundidad_cen + profundidad_ext) / 3;

        // Detect irregular wear: if difference between max and min > 30% of average
        const maxVal = Math.max(profundidad_int, profundidad_cen, profundidad_ext);
        const minVal = Math.min(profundidad_int, profundidad_cen, profundidad_ext);
        const desgasteIrregular = profundidadProm > 0 ? (maxVal - minVal) / profundidadProm > 0.3 : false;

        // Determine wear type
        let tipoDesgaste: string | null = null;
        if (desgasteIrregular) {
            if (profundidad_cen < profundidad_int && profundidad_cen < profundidad_ext) {
                tipoDesgaste = 'CENTRO';
            } else if (profundidad_int < profundidad_cen && profundidad_int < profundidad_ext) {
                tipoDesgaste = 'INTERIOR';
            } else if (profundidad_ext < profundidad_int && profundidad_ext < profundidad_cen) {
                tipoDesgaste = 'EXTERIOR';
            } else {
                tipoDesgaste = 'DIAGONAL';
            }
        }

        const medicion = await prisma.medicionProfundidad.create({
            data: {
                neumatico_id: validated.neumatico_id,
                evento_id: validated.evento_id || null,
                fecha_medicion: new Date(),
                profundidad_int: new Prisma.Decimal(profundidad_int),
                profundidad_cen: new Prisma.Decimal(profundidad_cen),
                profundidad_ext: new Prisma.Decimal(profundidad_ext),
                profundidad_prom: new Prisma.Decimal(profundidadProm),
                desgaste_irregular: desgasteIrregular,
                tipo_desgaste: tipoDesgaste,
                observaciones: validated.observaciones || null,
                kilometraje: validated.kilometraje ? new Prisma.Decimal(validated.kilometraje) : null,
                creado_por: usuarioId,
            },
        });

        // Update the tire's current depth values
        await prisma.neumatico.update({
            where: { id: validated.neumatico_id },
            data: {
                profundidad_remanente_actual_mm: new Prisma.Decimal(profundidadProm),
                profundidad_int: new Prisma.Decimal(profundidad_int),
                profundidad_cen: new Prisma.Decimal(profundidad_cen),
                profundidad_ext: new Prisma.Decimal(profundidad_ext),
                fecha_ultima_medicion_profundidad: new Date(),
            },
        });

        return this.toResult(medicion);
    }

    /**
     * Get latest measurement for a specific tire
     */
    async getByNeumatico(neumaticoId: string): Promise<MedicionProfundidadResult | null> {
        const medicion = await prisma.medicionProfundidad.findFirst({
            where: { neumatico_id: neumaticoId },
            orderBy: { fecha_medicion: 'desc' },
        });

        if (!medicion) return null;
        return this.toResult(medicion);
    }

    /**
     * Get measurement history for a tire
     */
    async getHistorial(
        neumaticoId: string,
        limit: number = 50,
        offset: number = 0
    ): Promise<{ measurements: MedicionHistorialItem[]; total: number }> {
        const [measurements, total] = await Promise.all([
            prisma.medicionProfundidad.findMany({
                where: { neumatico_id: neumaticoId },
                orderBy: { fecha_medicion: 'desc' },
                skip: offset,
                take: limit,
            }),
            prisma.medicionProfundidad.count({
                where: { neumatico_id: neumaticoId },
            }),
        ]);

        return {
            measurements: measurements.map((m) => ({
                id: m.id,
                fecha_medicion: m.fecha_medicion,
                profundidad_int: Number(m.profundidad_int),
                profundidad_cen: Number(m.profundidad_cen),
                profundidad_ext: Number(m.profundidad_ext),
                profundidad_prom: Number(m.profundidad_prom),
                desgaste_irregular: m.desgaste_irregular,
                tipo_desgaste: m.tipo_desgaste,
                observaciones: m.observaciones,
                kilometraje: m.kilometraje ? Number(m.kilometraje) : null,
                creado_por: m.creado_por,
            })),
            total,
        };
    }

    /**
     * Get all measurements for a company with pagination
     */
    async getAllByEmpresa(
        empresaId: string,
        limit: number = 50,
        offset: number = 0
    ): Promise<{ measurements: MedicionProfundidadResult[]; total: number }> {
        const [measurements, total] = await Promise.all([
            prisma.medicionProfundidad.findMany({
                where: {
                    neumatico: {
                        empresa_id: empresaId,
                    },
                },
                orderBy: { fecha_medicion: 'desc' },
                skip: offset,
                take: limit,
            }),
            prisma.medicionProfundidad.count({
                where: {
                    neumatico: {
                        empresa_id: empresaId,
                    },
                },
            }),
        ]);

        return {
            measurements: measurements.map((m) => this.toResult(m)),
            total,
        };
    }

    private toResult(medicion: any): MedicionProfundidadResult {
        return {
            id: medicion.id,
            neumatico_id: medicion.neumatico_id,
            evento_id: medicion.evento_id,
            fecha_medicion: medicion.fecha_medicion,
            profundidad_int: Number(medicion.profundidad_int),
            profundidad_cen: Number(medicion.profundidad_cen),
            profundidad_ext: Number(medicion.profundidad_ext),
            profundidad_prom: Number(medicion.profundidad_prom),
            desgaste_irregular: medicion.desgaste_irregular,
            tipo_desgaste: medicion.tipo_desgaste,
            observaciones: medicion.observaciones,
            kilometraje: medicion.kilometraje ? Number(medicion.kilometraje) : null,
            creado_por: medicion.creado_por,
            creado_en: medicion.creado_en,
        };
    }
}

export const medicionProfundidadService = new MedicionProfundidadService();
