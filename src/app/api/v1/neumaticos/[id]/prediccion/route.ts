import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import prisma from '@/lib/prisma';

/**
 * @swagger
 * /api/v1/neumaticos/{id}/prediccion:
 *   get:
 *     summary: Prediccion de vida util restante del neumatico
 *     tags: [Neumaticos]
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { id } = await params;

        // Obtener neumático con historial
        const neumatico = await prisma.neumatico.findFirst({
            where: {
                id,
                empresa_id: session.user.empresa_id!
            },
            include: {
                modelo: { select: { profundidad_original_mm: true, medida: true } },
                inspecciones: {
                    orderBy: { fecha_inspeccion: 'desc' },
                    take: 10
                }
            }
        });

        if (!neumatico) {
            return ApiResponseHelper.error('Neumático no encontrado', 404);
        }

        // Datos base
        const mmActual = Number(neumatico.profundidad_remanente_actual_mm);
        const mmRetiro = 3.0; // Profundidad mínima para retiro (estándar industria)
        const mmInicial = Number(neumatico.modelo?.profundidad_original_mm || 16);
        const kmAcumulado = Number(neumatico.kilometraje_acumulado);

        // Calcular tasa de desgaste histórica (mm/km)
        let tasaDesgaste = 0.000008; // Default: ~8mm por 1,000,000 km (conservador)

        if (kmAcumulado > 0 && mmInicial > mmActual) {
            const mmDesgastados = mmInicial - mmActual;
            tasaDesgaste = mmDesgastados / kmAcumulado;
        }

        // Si hay historial de inspecciones, calcular tasa más precisa
        if (neumatico.inspecciones.length >= 2) {
            const primeraInsp = neumatico.inspecciones[neumatico.inspecciones.length - 1];
            const ultimaInsp = neumatico.inspecciones[0];

            const mmDesdeInspecciones = Number(primeraInsp.mm_medido) - Number(ultimaInsp.mm_medido);
            const diasEntreinspecciones = Math.floor(
                (new Date(ultimaInsp.fecha_inspeccion).getTime() - new Date(primeraInsp.fecha_inspeccion).getTime())
                / (1000 * 60 * 60 * 24)
            );

            if (diasEntreinspecciones > 0 && mmDesdeInspecciones > 0) {
                // Calcular desgaste por día basado en inspecciones
                const mmPorDia = mmDesdeInspecciones / diasEntreinspecciones;
                tasaDesgaste = mmPorDia; // Usaremos mm/día para predicción basada en tiempo
            }
        }

        // Calcular predicciones
        const mmRestantes = mmActual - mmRetiro;
        let kmRestantes = 0;
        let diasRestantes = 0;
        let fechaEstimadaCambio: Date | null = null;

        if (tasaDesgaste > 0 && mmRestantes > 0) {
            // Si usamos tasa por km
            if (kmAcumulado > 0) {
                const tasaPorKm = (mmInicial - mmActual) / kmAcumulado;
                if (tasaPorKm > 0) {
                    kmRestantes = Math.round(mmRestantes / tasaPorKm);
                }
            }

            // Si usamos tasa por día (más preciso con inspecciones)
            if (neumatico.inspecciones.length >= 2) {
                diasRestantes = Math.round(mmRestantes / tasaDesgaste);
                fechaEstimadaCambio = new Date();
                fechaEstimadaCambio.setDate(fechaEstimadaCambio.getDate() + diasRestantes);
            } else if (kmRestantes > 0) {
                // Estimar días basado en km promedio diario (asumimos 200 km/día para flotas)
                const kmPromedioDiario = 200;
                diasRestantes = Math.round(kmRestantes / kmPromedioDiario);
                fechaEstimadaCambio = new Date();
                fechaEstimadaCambio.setDate(fechaEstimadaCambio.getDate() + diasRestantes);
            }
        }

        // Determinar estado del neumático
        let estadoVida: 'OPTIMO' | 'BUENO' | 'PRECAUCION' | 'CRITICO' = 'OPTIMO';
        const porcentajeVidaRestante = (mmRestantes / (mmInicial - mmRetiro)) * 100;

        if (porcentajeVidaRestante <= 0) estadoVida = 'CRITICO';
        else if (porcentajeVidaRestante <= 20) estadoVida = 'PRECAUCION';
        else if (porcentajeVidaRestante <= 50) estadoVida = 'BUENO';

        return ApiResponseHelper.success({
            neumatico_id: id,
            medida: neumatico.modelo?.medida || 'N/A',

            // Estado actual
            mm_actual: mmActual,
            mm_retiro: mmRetiro,
            mm_restantes: Math.max(0, mmRestantes),
            porcentaje_vida_restante: Math.max(0, Math.round(porcentajeVidaRestante)),
            estado: estadoVida,

            // Predicciones
            km_restantes_estimado: Math.max(0, kmRestantes),
            dias_restantes_estimado: Math.max(0, diasRestantes),
            fecha_estimada_cambio: fechaEstimadaCambio?.toISOString().split('T')[0] || null,

            // Métricas de cálculo
            inspecciones_usadas: neumatico.inspecciones.length,
            confianza: neumatico.inspecciones.length >= 3 ? 'ALTA' :
                neumatico.inspecciones.length >= 1 ? 'MEDIA' : 'BAJA'
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
