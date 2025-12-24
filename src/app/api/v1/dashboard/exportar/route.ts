import { NextRequest, NextResponse } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { DashboardService } from '@/lib/services/dashboard.service';

const service = new DashboardService();

/**
 * @swagger
 * /api/v1/dashboard/exportar:
 *   get:
 *     summary: Exportar reporte a CSV
 *     description: Genera archivo CSV descargable con datos del reporte seleccionado
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: tipo
 *         required: true
 *         schema:
 *           type: string
 *           enum: [inventario, rendimiento, desechos]
 *     responses:
 *       200:
 *         description: Archivo CSV
 *         content:
 *           text/csv:
 *             schema:
 *               type: string
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const tipo = searchParams.get('tipo');

        if (!tipo || !['inventario', 'rendimiento', 'desechos'].includes(tipo)) {
            return new NextResponse('Tipo de reporte inválido. Use: inventario, rendimiento, desechos', { status: 400 });
        }

        let csv = '';
        let filename = '';

        if (tipo === 'inventario') {
            const reporte = await service.getReporteInventario();
            csv = 'Almacen,Estado,Modelo,Medida,Cantidad\n';
            reporte.detalle.forEach(d => {
                csv += `"${d.almacen?.nombre || 'N/A'}","${d.estado}","${d.modelo.nombre}","${d.modelo.medida}",${d.cantidad}\n`;
            });
            filename = 'inventario_neumaticos.csv';
        }
        else if (tipo === 'rendimiento') {
            const reporte = await service.getReporteRendimiento(50);
            csv = 'Numero Serie,Modelo,CPK,Kilometraje,Estado,Ranking\n';
            reporte.top_mejores.forEach((n, i) => {
                csv += `"${n.numero_serie}","${n.modelo}",${n.cpk},${n.kilometraje},"${n.estado}","Top ${i + 1}"\n`;
            });
            reporte.top_peores.forEach((n, i) => {
                csv += `"${n.numero_serie}","${n.modelo}",${n.cpk},${n.kilometraje},"${n.estado}","Peor ${i + 1}"\n`;
            });
            filename = 'rendimiento_cpk.csv';
        }
        else if (tipo === 'desechos') {
            const reporte = await service.getReporteDesechos();
            csv = 'Motivo,Cantidad,Porcentaje\n';
            reporte.por_motivo.forEach(m => {
                csv += `"${m.motivo}",${m.cantidad},${m.porcentaje}%\n`;
            });
            csv += '\nMes,Cantidad\n';
            reporte.por_mes.forEach(m => {
                csv += `"${m.mes}",${m.cantidad}\n`;
            });
            filename = 'desechos_neumaticos.csv';
        }

        return new NextResponse(csv, {
            status: 200,
            headers: {
                'Content-Type': 'text/csv; charset=utf-8',
                'Content-Disposition': `attachment; filename="${filename}"`
            }
        });
    } catch (error) {
        console.error('Error exportando CSV:', error);
        return new NextResponse('Error generando reporte', { status: 500 });
    }
}
