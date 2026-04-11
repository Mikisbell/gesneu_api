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
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION);

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

        // ✅ Fase 6B.2: Alertas Post-Inspección
        // Valores canónicos del schema: TipoAlertaEnum y SeveridadAlertaEnum
        const alertas: Array<{
            tipo: 'PROFUNDIDAD_MINIMA' | 'REENCAUCHE_MAXIMO' | 'DESGASTE_IRREGULAR' | 'VENCIMIENTO_DOT' | 'PRESION_BAJA';
            mensaje: string;
            severidad: 'INFO' | 'WARNING' | 'CRITICAL';
        }> = [];

        // Obtener inspección anterior para comparar
        const inspeccionAnterior = await prisma.inspeccion.findFirst({
            where: {
                neumatico_id: data.neumatico_id,
                id: { not: inspeccion.id },
                fecha_inspeccion: { lt: inspeccion.fecha_inspeccion }
            },
            orderBy: { fecha_inspeccion: 'desc' }
        });

        if (inspeccionAnterior) {
            const psiAnterior = Number(inspeccionAnterior.psi_medido);
            const mmAnterior = Number(inspeccionAnterior.mm_medido);
            const psiActual = data.psi_medido;
            const mmActual = data.mm_medido;

            // 1. Anomalía de Presión: bajó >5%
            if (psiAnterior > 0) {
                const cambioPresion = ((psiAnterior - psiActual) / psiAnterior) * 100;
                if (cambioPresion >= 5) {
                    alertas.push({
                        tipo: 'PRESION_BAJA',
                        mensaje: `Presión bajó ${cambioPresion.toFixed(1)}% (de ${psiAnterior} a ${psiActual} PSI)`,
                        severidad: cambioPresion >= 10 ? 'CRITICAL' : 'WARNING'
                    });
                }
            }

            // 2. Desgaste Acelerado: bajó más de lo esperado
            // Calcular días entre inspecciones
            const diasTranscurridos = Math.floor(
                (new Date(inspeccion.fecha_inspeccion).getTime() - new Date(inspeccionAnterior.fecha_inspeccion).getTime())
                / (1000 * 60 * 60 * 24)
            );

            if (diasTranscurridos > 0 && mmAnterior > mmActual) {
                const desgasteMm = mmAnterior - mmActual;
                const desgastePorDia = desgasteMm / diasTranscurridos;
                // Promedio normal: ~0.01 mm/día (10mm en 1000 días ~= 3 años)
                const umbralNormal = 0.015; // mm por día

                if (desgastePorDia > umbralNormal) {
                    alertas.push({
                        tipo: 'DESGASTE_IRREGULAR',
                        mensaje: `Desgaste acelerado detectado: ${desgasteMm.toFixed(1)}mm en ${diasTranscurridos} días`,
                        severidad: desgastePorDia > umbralNormal * 2 ? 'CRITICAL' : 'WARNING'
                    });
                }
            }
        }

        // Crear alertas en base de datos
        for (const alerta of alertas) {
            await prisma.alerta.create({
                data: {
                    neumatico_id: data.neumatico_id,
                    vehiculo_id: data.vehiculo_id || neumatico.ubicacion_vehiculo_id,
                    tipo: alerta.tipo,
                    mensaje: alerta.mensaje,
                    severidad: alerta.severidad
                    // leida y resuelta defaultean a false en el schema
                    // (Alerta es tenant-neutral, el aislamiento se deriva via neumatico/vehiculo)
                }
            });
        }

        return ApiResponseHelper.created({
            ...inspeccion,
            alertas_generadas: alertas.length
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
