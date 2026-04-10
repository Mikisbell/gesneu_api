import { NextRequest, NextResponse } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { prisma } from '@/lib/prisma';

/**
 * @swagger
 * /api/v1/reportes/pareto:
 *   get:
 *     summary: Análisis Pareto de Fallas de Neumáticos
 *     description: >
 *       Returns Pareto analysis of tire failures grouped by failure category.
 *       Data is formatted for Pareto chart visualization with cumulative percentages.
 *       Queries eventos_neumaticos with motivo_desecho and categorizes by categoria_falla.
 *     tags:
 *       - Reportes
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: empresa_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Company ID (optional, defaults to authenticated user's empresa)
 *       - in: query
 *         name: fecha_desde
 *         schema:
 *           type: string
 *           format: date
 *         description: Start date for analysis (YYYY-MM-DD)
 *       - in: query
 *         name: fecha_hasta
 *         schema:
 *           type: string
 *           format: date
 *         description: End date for analysis (YYYY-MM-DD)
 *     responses:
 *       200:
 *         description: Pareto analysis results
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: object
 *                   properties:
 *                     total_fallas:
 *                       type: integer
 *                     categorias:
 *                       type: array
 *                       items:
 *                         type: object
 *                         properties:
 *                           categoria:
 *                             type: string
 *                           cantidad:
 *                             type: integer
 *                           porcentaje:
 *                             type: number
 *                           porcentaje_acumulado:
 *                             type: number
 *                     motivos_detalle:
 *                       type: array
 *                       items:
 *                         type: object
 *                         properties:
 *                           motivo:
 *                             type: string
 *                           categoria:
 *                             type: string
 *                           cantidad:
 *                             type: integer
 *                           porcentaje_acumulado:
 *                             type: number
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 *       500:
 *         description: Error interno del servidor
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.REPORTES_RENDIMIENTO);

        const { searchParams } = new URL(request.url);
        const fechaDesde = searchParams.get('fecha_desde');
        const fechaHasta = searchParams.get('fecha_hasta');

        const empresaId = session.user.empresa_id;
        if (!empresaId) {
            return NextResponse.json(
                { error: 'Usuario no tiene empresa asignada' },
                { status: 403 }
            );
        }

        // Build date filter
        const dateFilter: any = {};
        if (fechaDesde) {
            dateFilter.gte = new Date(fechaDesde);
        }
        if (fechaHasta) {
            dateFilter.lte = new Date(fechaHasta);
        }

        // Query eventos de desecho with motivo details
        const eventosDesecho = await prisma.eventoNeumatico.findMany({
            where: {
                tipo_evento: 'DESECHO',
                motivo_desecho_id: { not: null },
                neumatico: {
                    empresa_id: empresaId,
                },
                ...(Object.keys(dateFilter).length > 0 && {
                    fecha_evento: dateFilter,
                }),
            },
            include: {
                motivo_desecho: {
                    select: {
                        nombre: true,
                        categoria_falla: true,
                    },
                },
            },
        });

        if (eventosDesecho.length === 0) {
            return NextResponse.json({
                success: true,
                data: {
                    total_fallas: 0,
                    categorias: [],
                    motivos_detalle: [],
                },
            });
        }

        // Aggregate by categoria_falla
        const categoriaCount: Record<string, number> = {};
        const motivoCount: Record<string, { categoria: string; count: number }> = {};

        for (const evento of eventosDesecho) {
            const motivo = evento.motivo_desecho;
            if (!motivo) continue;

            const categoria = motivo.categoria_falla || 'SIN_CATEGORIA';
            const motivoNombre = motivo.nombre;

            // Count by category
            categoriaCount[categoria] = (categoriaCount[categoria] || 0) + 1;

            // Count by specific motivo
            if (!motivoCount[motivoNombre]) {
                motivoCount[motivoNombre] = { categoria, count: 0 };
            }
            motivoCount[motivoNombre].count++;
        }

        const totalFallas = eventosDesecho.length;

        // Build Pareto data for categories (sorted descending)
        const categoriasPareto = Object.entries(categoriaCount)
            .map(([categoria, cantidad]) => ({ categoria, cantidad }))
            .sort((a, b) => b.cantidad - a.cantidad);

        let acumuladoCat = 0;
        const categoriasConPorcentaje = categoriasPareto.map((item) => {
            const porcentaje = (item.cantidad / totalFallas) * 100;
            acumuladoCat += porcentaje;
            return {
                categoria: item.categoria,
                cantidad: item.cantidad,
                porcentaje: Math.round(porcentaje * 100) / 100,
                porcentaje_acumulado: Math.round(acumuladoCat * 100) / 100,
            };
        });

        // Build Pareto data for motivos (sorted descending)
        const motivosPareto = Object.entries(motivoCount)
            .map(([motivo, data]) => ({ motivo, categoria: data.categoria, cantidad: data.count }))
            .sort((a, b) => b.cantidad - a.cantidad);

        let acumuladoMot = 0;
        const motivosConPorcentaje = motivosPareto.map((item) => {
            const porcentaje = (item.cantidad / totalFallas) * 100;
            acumuladoMot += porcentaje;
            return {
                motivo: item.motivo,
                categoria: item.categoria,
                cantidad: item.cantidad,
                porcentaje: Math.round(porcentaje * 100) / 100,
                porcentaje_acumulado: Math.round(acumuladoMot * 100) / 100,
            };
        });

        return NextResponse.json({
            success: true,
            data: {
                total_fallas: totalFallas,
                categorias: categoriasConPorcentaje,
                motivos_detalle: motivosConPorcentaje,
            },
        });
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }
        if (error.message === 'FORBIDDEN') {
            return NextResponse.json({ error: 'Permisos insuficientes' }, { status: 403 });
        }
        console.error('[PARETO] Error:', error);
        return NextResponse.json(
            { error: 'Error interno del servidor' },
            { status: 500 }
        );
    }
}
