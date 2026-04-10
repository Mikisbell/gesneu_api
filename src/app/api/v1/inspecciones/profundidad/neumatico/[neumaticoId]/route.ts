import { NextRequest, NextResponse } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { medicionProfundidadService } from '@/lib/services/medicion-profundidad.service';
import { prisma } from '@/lib/prisma';

/**
 * @swagger
 * /api/v1/inspecciones/profundidad/neumatico/{neumaticoId}:
 *   get:
 *     summary: Historial de Profundidad por Neumático
 *     description: >
 *       Returns the complete depth measurement history for a specific tire.
 *       Results are ordered by measurement date descending (most recent first).
 *       Supports pagination with limit and offset query parameters.
 *     tags:
 *       - Inspecciones
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: neumaticoId
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del neumático
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *         description: Number of results per page
 *       - in: query
 *         name: offset
 *         schema:
 *           type: integer
 *           default: 0
 *         description: Number of results to skip
 *     responses:
 *       200:
 *         description: Measurement history for the tire
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                       fecha_medicion:
 *                         type: string
 *                         format: date-time
 *                       profundidad_int:
 *                         type: number
 *                       profundidad_cen:
 *                         type: number
 *                       profundidad_ext:
 *                         type: number
 *                       profundidad_prom:
 *                         type: number
 *                       desgaste_irregular:
 *                         type: boolean
 *                       tipo_desgaste:
 *                         type: string
 *                         nullable: true
 *                       observaciones:
 *                         type: string
 *                         nullable: true
 *                       kilometraje:
 *                         type: number
 *                         nullable: true
 *                 total:
 *                   type: integer
 *       404:
 *         description: Neumático no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 *       500:
 *         description: Error interno del servidor
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ neumaticoId: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        if (!session.user.empresa_id) {
            return NextResponse.json(
                { error: 'Usuario no tiene empresa asignada' },
                { status: 403 }
            );
        }

        const { neumaticoId } = await params;

        // Verify tire exists and belongs to user's company
        const neumatico = await prisma.neumatico.findUnique({
            where: {
                id: neumaticoId,
                empresa_id: session.user.empresa_id,
            },
        });

        if (!neumatico) {
            return NextResponse.json(
                { error: 'Neumático no encontrado o no pertenece a su empresa' },
                { status: 404 }
            );
        }

        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '50');
        const offset = parseInt(searchParams.get('offset') || '0');

        const history = await medicionProfundidadService.getHistorial(
            neumaticoId,
            limit,
            offset
        );

        return NextResponse.json({
            success: true,
            data: history.measurements,
            total: history.total,
        });
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }
        if (error.message === 'FORBIDDEN') {
            return NextResponse.json({ error: 'Permisos insuficientes' }, { status: 403 });
        }
        console.error('[API] Error al obtener historial de profundidad:', error);
        return NextResponse.json(
            { error: 'Error interno del servidor' },
            { status: 500 }
        );
    }
}
