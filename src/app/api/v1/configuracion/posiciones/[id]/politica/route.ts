import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';

/**
 * @swagger
 * /api/v1/configuracion/posiciones/{id}/politica:
 *   patch:
 *     summary: Actualizar política de reencauchado de una posición
 *     description: Configura si una posición específica permite neumáticos reencauchados
 *     tags:
 *       - Configuración
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID de la posición de neumático
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               permite_reencauchado:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Política actualizada
 */
export async function PATCH(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.VEHICULOS_UPDATE); // Admin/Gestor

        const { id } = await params;
        const body = await request.json();

        if (typeof body.permite_reencauchado !== 'boolean') {
            return ApiResponseHelper.error('permite_reencauchado debe ser boolean', 400);
        }

        const posicion = await prisma.posicionNeumatico.update({
            where: { id },
            data: { permite_reencauchado: body.permite_reencauchado },
            include: {
                configuracion_eje: {
                    select: { tipo_eje: true, numero_eje: true }
                }
            }
        });

        return ApiResponseHelper.success(posicion, `Política actualizada para posición ${posicion.numero_posicion}`);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/configuracion/posiciones/{id}/politica:
 *   get:
 *     summary: Obtener política de reencauchado de una posición
 *     tags:
 *       - Configuración
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Política de la posición
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.VEHICULOS_READ);

        const { id } = await params;

        const posicion = await prisma.posicionNeumatico.findUnique({
            where: { id },
            include: {
                configuracion_eje: {
                    select: {
                        tipo_eje: true,
                        numero_eje: true,
                        permite_reencauchados: true
                    }
                }
            }
        });

        if (!posicion) {
            return ApiResponseHelper.error('Posición no encontrada', 404);
        }

        return ApiResponseHelper.success({
            posicion_id: posicion.id,
            numero_posicion: posicion.numero_posicion,
            lado: posicion.lado_vehiculo,
            permite_reencauchado: posicion.permite_reencauchado,
            eje: {
                tipo: posicion.configuracion_eje.tipo_eje,
                numero: posicion.configuracion_eje.numero_eje,
                permite_reencauchados: posicion.configuracion_eje.permite_reencauchados
            }
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
