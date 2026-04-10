import { NextRequest, NextResponse } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { InspeccionService } from '@/lib/services/inspeccion.service';
import { medicionProfundidadService } from '@/lib/services/medicion-profundidad.service';
import { CreateMedicionProfundidadSchema } from '@/lib/validators/medicion-profundidad.validator';
import { registerObservers } from '@/lib/events/registry';

// Ensure observers are registered
registerObservers();

const inspeccionService = new InspeccionService();

/**
 * @swagger
 * /api/v1/inspecciones/profundidad:
 *   get:
 *     summary: Listar Mediciones de Profundidad
 *     description: Returns a paginated list of depth measurements for the authenticated user's company.
 *     tags:
 *       - Inspecciones
 *     security:
 *       - bearerAuth: []
 *     parameters:
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
 *         description: List of depth measurements
 *       401:
 *         description: No autenticado
 *   post:
 *     summary: Registrar Medición de Profundidad Detallada
 *     description: >
 *       Creates a detailed depth measurement record for a tire with interior, center, and exterior readings.
 *       Automatically calculates average, detects irregular wear, and determines wear type.
 *       Also updates the tire's current depth values.
 *     tags:
 *       - Inspecciones
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - neumatico_id
 *               - profundidad_int
 *               - profundidad_cen
 *               - profundidad_ext
 *             properties:
 *               neumatico_id:
 *                 type: string
 *                 format: uuid
 *               profundidad_int:
 *                 type: number
 *                 description: Interior tread depth in mm
 *               profundidad_cen:
 *                 type: number
 *                 description: Center tread depth in mm
 *               profundidad_ext:
 *                 type: number
 *                 description: Exterior tread depth in mm
 *               kilometraje:
 *                 type: number
 *               observaciones:
 *                 type: string
 *               evento_id:
 *                 type: string
 *                 format: uuid
 *     responses:
 *       201:
 *         description: Measurement created successfully
 *       400:
 *         description: Invalid data
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
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '50');
        const offset = parseInt(searchParams.get('offset') || '0');

        if (!session.user.empresa_id) {
            return NextResponse.json(
                { error: 'Usuario no tiene empresa asignada' },
                { status: 403 }
            );
        }

        const result = await medicionProfundidadService.getAllByEmpresa(
            session.user.empresa_id,
            limit,
            offset
        );

        return NextResponse.json({
            success: true,
            data: result.measurements,
            total: result.total,
        });
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }
        if (error.message === 'FORBIDDEN') {
            return NextResponse.json({ error: 'Permisos insuficientes' }, { status: 403 });
        }
        console.error('[API] Error al listar mediciones de profundidad:', error);
        return NextResponse.json(
            { error: 'Error interno del servidor' },
            { status: 500 }
        );
    }
}

export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION);

        const body = await request.json();

        const validation = CreateMedicionProfundidadSchema.safeParse(body);
        if (!validation.success) {
            return NextResponse.json(
                {
                    error: 'Datos inválidos',
                    detalles: validation.error.errors.map((e) => ({
                        campo: e.path.join('.'),
                        mensaje: e.message,
                    })),
                },
                { status: 400 }
            );
        }

        if (!session.user.empresa_id) {
            return NextResponse.json(
                { error: 'Usuario no tiene empresa asignada' },
                { status: 403 }
            );
        }

        const medicion = await medicionProfundidadService.create(
            validation.data,
            session.user.id,
            session.user.empresa_id
        );

        return NextResponse.json(
            {
                success: true,
                data: medicion,
                message: 'Medición de profundidad registrada correctamente',
            },
            { status: 201 }
        );
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return NextResponse.json({ error: 'No autenticado' }, { status: 401 });
        }
        if (error.message === 'FORBIDDEN') {
            return NextResponse.json({ error: 'Permisos insuficientes' }, { status: 403 });
        }
        console.error('[API] Error en registro de profundidad:', error);
        return NextResponse.json(
            { error: error.message || 'Error interno' },
            { status: 500 }
        );
    }
}
