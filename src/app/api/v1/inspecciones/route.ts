import { NextRequest } from 'next/server';
import { z } from 'zod';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import prisma from '@/lib/prisma';
import { Prisma } from '@prisma/client';

const createInspeccionSchema = z.object({
    neumatico_id: z.string().uuid(),
    vehiculo_id: z.string().uuid().optional(),
    posicion_codigo: z.string().max(10).optional(),
    psi_medido: z.number().min(0).max(200),
    mm_medido: z.number().min(0).max(30),
    mm_interior: z.number().min(0).max(30).optional(),
    mm_centro: z.number().min(0).max(30).optional(),
    mm_exterior: z.number().min(0).max(30).optional(),
    foto_url: z.string().url().optional(),
    observaciones: z.string().max(500).optional(),
    fuente: z.enum(['MANUAL', 'SENSOR_TPMS']).default('MANUAL'),
});

/**
 * @swagger
 * /api/v1/inspecciones:
 *   get:
 *     summary: Lista inspecciones con filtros opcionales
 *     tags: [Inspecciones]
 *     parameters:
 *       - in: query
 *         name: neumatico_id
 *         schema:
 *           type: string
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *   post:
 *     summary: Registrar una nueva inspeccion
 *     tags: [Inspecciones]
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const neumaticoId = searchParams.get('neumatico_id');
        const limit = parseInt(searchParams.get('limit') || '50', 10);

        const inspecciones = await prisma.inspeccion.findMany({
            where: {
                empresa_id: session.user.empresa_id!,
                ...(neumaticoId ? { neumatico_id: neumaticoId } : {})
            },
            include: {
                neumatico: { select: { numero_serie: true } },
                inspector: { select: { nombre_completo: true } }
            },
            orderBy: { fecha_inspeccion: 'desc' },
            take: limit
        });

        return ApiResponseHelper.success(inspecciones);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_WRITE);

        const body = await request.json();
        const data = createInspeccionSchema.parse(body);

        // Verificar que el neumático pertenece a la empresa
        const neumatico = await prisma.neumatico.findFirst({
            where: {
                id: data.neumatico_id,
                empresa_id: session.user.empresa_id!
            }
        });

        if (!neumatico) {
            return ApiResponseHelper.error('Neumático no encontrado', 404);
        }

        // Crear inspección
        const inspeccion = await prisma.inspeccion.create({
            data: {
                neumatico_id: data.neumatico_id,
                vehiculo_id: data.vehiculo_id,
                posicion_codigo: data.posicion_codigo,
                empresa_id: session.user.empresa_id!,
                psi_medido: new Prisma.Decimal(data.psi_medido),
                mm_medido: new Prisma.Decimal(data.mm_medido),
                mm_interior: data.mm_interior ? new Prisma.Decimal(data.mm_interior) : null,
                mm_centro: data.mm_centro ? new Prisma.Decimal(data.mm_centro) : null,
                mm_exterior: data.mm_exterior ? new Prisma.Decimal(data.mm_exterior) : null,
                foto_url: data.foto_url,
                observaciones: data.observaciones,
                fuente: data.fuente,
                inspector_id: session.user.id
            },
            include: {
                neumatico: { select: { numero_serie: true } },
                inspector: { select: { nombre_completo: true } }
            }
        });

        // Actualizar último estado del neumático
        await prisma.neumatico.update({
            where: { id: data.neumatico_id },
            data: {
                presion_actual_psi: new Prisma.Decimal(data.psi_medido),
                profundidad_remanente_actual_mm: new Prisma.Decimal(data.mm_medido),
                profundidad_int: data.mm_interior ? new Prisma.Decimal(data.mm_interior) : undefined,
                profundidad_cen: data.mm_centro ? new Prisma.Decimal(data.mm_centro) : undefined,
                profundidad_ext: data.mm_exterior ? new Prisma.Decimal(data.mm_exterior) : undefined,
                fecha_ultima_medicion_profundidad: new Date()
            }
        });

        return ApiResponseHelper.created(inspeccion);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
