import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params;

        // Validar que el neumático exista
        const neumatico = await prisma.neumatico.findUnique({
            where: { id },
            select: { id: true }
        });

        if (!neumatico) {
            return ApiResponseHelper.error('Neumático no encontrado', 404);
        }

        // Obtener historial (últimas 20 lecturas)
        const historial = await prisma.lecturaPresion.findMany({
            where: { neumatico_id: id },
            orderBy: { fecha_lectura: 'desc' }, // Traer las más recientes primero
            take: 20,
            include: {
                usuario: {
                    select: { username: true, nombre_completo: true }
                }
            }
        });

        // Formatear para el frontend (más antiguas a la izquierda, más recientes a la derecha)
        // Chart.js espera el eje X en orden cronológico ascendente.
        const chartData = historial.reverse().map(lectura => ({
            id: lectura.id,
            fecha: lectura.fecha_lectura.toISOString(),
            presion: lectura.presion_psi,
            temperatura: lectura.temperatura_c,
            fuente: lectura.fuente,
            inspector: lectura.usuario?.nombre_completo || 'Sistema'
        }));

        return ApiResponseHelper.success(chartData);

    } catch (error: any) {
        return ApiResponseHelper.error(error.message, 500);
    }
}
