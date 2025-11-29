import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

/**
 * @swagger
 * /api/v1/catalogos/modelos-neumatico:
 *   get:
 *     summary: Listar modelos de neumáticos
 *     description: Obtiene una lista de todos los modelos de neumáticos activos.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de modelos recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/ModeloNeumatico'
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization (Usamos NEUMATICOS_READ ya que es intrínseco)
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        // 3. Business logic
        const modelos = await prisma.modeloNeumatico.findMany({
            include: {
                fabricante: true
            },
            orderBy: {
                nombre: 'asc'
            }
        })

        return ApiResponseHelper.success(modelos)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
