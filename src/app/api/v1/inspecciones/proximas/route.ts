import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import prisma from '@/lib/prisma';

/**
 * @swagger
 * /api/v1/inspecciones/proximas:
 *   get:
 *     summary: Lista neumaticos que requieren inspeccion pronto
 *     tags: [Inspecciones]
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '20', 10);

        // Obtener neumáticos activos con su última inspección y alertas
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                empresa_id: session.user.empresa_id!,
                activo: true,
                estado_actual: { in: ['EN_SERVICIO', 'EN_STOCK'] }
            },
            include: {
                modelo: { select: { medida: true, fabricante: { select: { nombre: true } } } },
                ubicacion_vehiculo: { select: { placa: true, numero_economico: true } },
                inspecciones: {
                    orderBy: { fecha_inspeccion: 'desc' },
                    take: 1
                },
                alertas: {
                    where: { estado: 'PENDIENTE' },
                    take: 5
                }
            }
        });

        // Calcular frecuencia de inspección adaptativa para cada neumático
        const proximas = neumaticos.map(n => {
            const ultimaInspeccion = n.inspecciones[0];
            const diasDesdeInspeccion = ultimaInspeccion
                ? Math.floor((Date.now() - new Date(ultimaInspeccion.fecha_inspeccion).getTime()) / (1000 * 60 * 60 * 24))
                : 999;

            // Frecuencia base: 30 días
            let frecuenciaRecomendadaDias = 30;

            // Factor 1: Estado de vida restante
            const mmActual = Number(n.profundidad_remanente_actual_mm);
            if (mmActual <= 3) frecuenciaRecomendadaDias = 7; // Crítico
            else if (mmActual <= 5) frecuenciaRecomendadaDias = 14; // Precaución
            else if (mmActual <= 7) frecuenciaRecomendadaDias = 21;

            // Factor 2: Anomalías previas
            if (n.alertas.length > 0) {
                frecuenciaRecomendadaDias = Math.min(frecuenciaRecomendadaDias, 14);
            }

            // Factor 3: Kilometraje alto
            const kmAcumulado = Number(n.kilometraje_acumulado);
            if (kmAcumulado > 100000) {
                frecuenciaRecomendadaDias = Math.min(frecuenciaRecomendadaDias, 21);
            }

            // Calcular días vencido (negativo = faltan días, positivo = vencido)
            const diasVencido = diasDesdeInspeccion - frecuenciaRecomendadaDias;
            const fechaProximaInspeccion = new Date();

            if (ultimaInspeccion) {
                const fechaBase = new Date(ultimaInspeccion.fecha_inspeccion);
                fechaBase.setDate(fechaBase.getDate() + frecuenciaRecomendadaDias);
                fechaProximaInspeccion.setTime(fechaBase.getTime());
            }

            // Determinar urgencia
            let urgencia: 'VENCIDA' | 'HOY' | 'PROXIMA' | 'NORMAL' = 'NORMAL';
            if (diasVencido > 0) urgencia = 'VENCIDA';
            else if (diasVencido === 0) urgencia = 'HOY';
            else if (diasVencido >= -3) urgencia = 'PROXIMA';

            return {
                neumatico_id: n.id,
                numero_serie: n.numero_serie,
                marca: n.modelo?.fabricante?.nombre || 'N/A',
                medida: n.modelo?.medida || 'N/A',
                placa: n.ubicacion_vehiculo?.placa || n.ubicacion_vehiculo?.numero_economico || 'Sin asignar',

                // Estado actual
                mm_actual: mmActual,
                alertas_pendientes: n.alertas.length,
                estado: n.estado_actual,

                // Inspección
                ultima_inspeccion: ultimaInspeccion?.fecha_inspeccion.toISOString().split('T')[0] || null,
                dias_desde_inspeccion: diasDesdeInspeccion === 999 ? null : diasDesdeInspeccion,
                frecuencia_recomendada_dias: frecuenciaRecomendadaDias,
                proxima_inspeccion: fechaProximaInspeccion.toISOString().split('T')[0],
                dias_vencido: diasVencido,
                urgencia
            };
        })
            // Ordenar por urgencia (vencidos primero, luego por días vencido descendente)
            .sort((a, b) => {
                const ordenUrgencia = { 'VENCIDA': 0, 'HOY': 1, 'PROXIMA': 2, 'NORMAL': 3 };
                if (ordenUrgencia[a.urgencia] !== ordenUrgencia[b.urgencia]) {
                    return ordenUrgencia[a.urgencia] - ordenUrgencia[b.urgencia];
                }
                return (b.dias_vencido || 0) - (a.dias_vencido || 0);
            })
            .slice(0, limit);

        // Resumen
        const resumen = {
            total: proximas.length,
            vencidas: proximas.filter(p => p.urgencia === 'VENCIDA').length,
            hoy: proximas.filter(p => p.urgencia === 'HOY').length,
            proximas: proximas.filter(p => p.urgencia === 'PROXIMA').length
        };

        return ApiResponseHelper.success({ resumen, proximas });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
