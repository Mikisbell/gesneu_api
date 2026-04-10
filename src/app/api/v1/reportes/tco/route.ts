import { NextRequest, NextResponse } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { prisma } from '@/lib/prisma';
import { TcoService } from '@/lib/services/tco.service';

/**
 * @swagger
 * /api/v1/reportes/tco:
 *   get:
 *     summary: Total Cost of Ownership Analysis
 *     description: >
 *       Returns aggregated TCO metrics for all tires in a company within the specified date range.
 *       Includes total cost, cost per kilometer, fuel waste estimates, and per-tire breakdown.
 *     tags:
 *       - Reportes
 *     security:
 *       - bearerAuth: []
 *     parameters:
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
 *         description: TCO analysis results
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
 *                     resumen:
 *                       type: object
 *                       properties:
 *                         total_neumaticos:
 *                           type: integer
 *                         costo_total_compra:
 *                           type: number
 *                         costo_total_mantenimiento:
 *                           type: number
 *                         tco_promedio:
 *                           type: number
 *                         cpk_promedio:
 *                           type: number
 *                         fuel_waste_total:
 *                           type: number
 *                     por_estado:
 *                       type: array
 *                       items:
 *                         type: object
 *                         properties:
 *                           estado:
 *                             type: string
 *                           cantidad:
 *                             type: integer
 *                           tco_promedio:
 *                             type: number
 *                     detalle_neumaticos:
 *                       type: array
 *                       items:
 *                         type: object
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

        // Fetch all tires for this company
        const neumaticos = await prisma.neumatico.findMany({
            where: {
                empresa_id: empresaId,
                activo: true,
                ...(Object.keys(dateFilter).length > 0 && {
                    creado_en: dateFilter,
                }),
            },
            select: {
                id: true,
                estado_actual: true,
                costo_compra: true,
                moneda_compra: true,
                kilometraje_acumulado: true,
                vida_util_restante_km: true,
            },
        });

        if (neumaticos.length === 0) {
            return NextResponse.json({
                success: true,
                data: {
                    resumen: {
                        total_neumaticos: 0,
                        costo_total_compra: 0,
                        costo_total_mantenimiento: 0,
                        tco_promedio: 0,
                        cpk_promedio: 0,
                        fuel_waste_total: 0,
                    },
                    por_estado: [],
                    detalle_neumaticos: [],
                },
            });
        }

        // Calculate financials for each tire
        const detalleNeumaticos: any[] = [];
        let costoTotalCompra = 0;
        let costoTotalMantenimiento = 0;
        let fuelWasteTotal = 0;
        let cpkSum = 0;
        let cpkCount = 0;

        const estadoMap: Record<string, { cantidad: number; tcoSum: number }> = {};

        for (const neum of neumaticos) {
            try {
                const financials = await TcoService.getFinancials(neum.id);

                costoTotalCompra += financials.costo_compra;
                costoTotalMantenimiento += financials.costo_mantenimiento;
                fuelWasteTotal += financials.fuel_waste_estimated_usd;

                if (financials.cpk > 0) {
                    cpkSum += financials.cpk;
                    cpkCount++;
                }

                const estado = neum.estado_actual;
                if (!estadoMap[estado]) {
                    estadoMap[estado] = { cantidad: 0, tcoSum: 0 };
                }
                estadoMap[estado].cantidad++;
                estadoMap[estado].tcoSum += financials.tco;

                detalleNeumaticos.push({
                    neumatico_id: neum.id,
                    estado: neum.estado_actual,
                    tco: financials.tco,
                    cpk: financials.cpk,
                    cpk_projected: financials.cpk_projected,
                    costo_compra: financials.costo_compra,
                    costo_mantenimiento: financials.costo_mantenimiento,
                    fuel_waste_estimated: financials.fuel_waste_estimated_usd,
                    kilometraje_acumulado: Number(neum.kilometraje_acumulado) || 0,
                    moneda: financials.currency,
                });
            } catch (err) {
                // If individual tire calculation fails, skip it
                console.error(`[TCO] Error calculating tire ${neum.id}:`, err);
            }
        }

        const totalNeumaticos = detalleNeumaticos.length;
        const tcoTotal = costoTotalCompra + costoTotalMantenimiento;
        const tcoPromedio = totalNeumaticos > 0 ? tcoTotal / totalNeumaticos : 0;
        const cpkPromedio = cpkCount > 0 ? cpkSum / cpkCount : 0;

        const porEstado = Object.entries(estadoMap).map(([estado, data]) => ({
            estado,
            cantidad: data.cantidad,
            tco_promedio: data.cantidad > 0 ? data.tcoSum / data.cantidad : 0,
        }));

        return NextResponse.json({
            success: true,
            data: {
                resumen: {
                    total_neumaticos: totalNeumaticos,
                    costo_total_compra: costoTotalCompra,
                    costo_total_mantenimiento: costoTotalMantenimiento,
                    tco_total: tcoTotal,
                    tco_promedio: tcoPromedio,
                    cpk_promedio: cpkPromedio,
                    fuel_waste_total: fuelWasteTotal,
                },
                por_estado: porEstado,
                detalle_neumaticos: detalleNeumaticos,
            },
        });
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }
        if (error.message === 'FORBIDDEN') {
            return NextResponse.json({ error: 'Permisos insuficientes' }, { status: 403 });
        }
        console.error('[TCO] Error:', error);
        return NextResponse.json(
            { error: 'Error interno del servidor' },
            { status: 500 }
        );
    }
}
