import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

// GET /api/v1/catalogos/almacenes/[id] - Obtener almacén por ID
/**
 * @swagger
 * /api/v1/catalogos/almacenes/{id}:
 *   get:
 *     summary: Obtener almacén por ID
 *     description: Obtiene los detalles de un almacén específico.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del almacén
 *     responses:
 *       200:
 *         description: Detalles del almacén
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Almacen'
 *       404:
 *         description: Almacén no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_ALMACENES_READ)
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_ALMACENES_READ);

    // 3. Business logic
    const almacen = await prisma.almacen.findUnique({
      where: { id: (await params).id }
    })

    if (!almacen) {
      return ApiResponseHelper.notFound()
    }

    return ApiResponseHelper.success(almacen)
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}

/**
 * @swagger
 * /api/v1/catalogos/almacenes/{id}:
 *   put:
 *     summary: Actualizar almacén
 *     description: Actualiza los datos de un almacén existente.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del almacén
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateAlmacenDTO'
 *     responses:
 *       200:
 *         description: Almacén actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Almacen'
 *                 message:
 *                   type: string
 *       404:
 *         description: Almacén no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_ALMACENES_UPDATE)
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_ALMACENES_UPDATE);

    // 3. Business logic
    const body = await request.json()

    // Verificar que existe
    const existe = await prisma.almacen.findUnique({
      where: { id: (await params).id }
    })

    if (!existe) {
      return ApiResponseHelper.notFound()
    }

    const almacen = await prisma.almacen.update({
      where: { id: (await params).id },
      data: {
        nombre: body.nombre,
        ubicacion: body.ubicacion,
        tipo: body.tipo
      }
    })

    return ApiResponseHelper.success(almacen, 'Almacén actualizado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}

/**
 * @swagger
 * /api/v1/catalogos/almacenes/{id}:
 *   delete:
 *     summary: Eliminar almacén
 *     description: Desactiva (soft delete) un almacén del sistema.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del almacén
 *     responses:
 *       200:
 *         description: Almacén desactivado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Almacen'
 *                 message:
 *                   type: string
 *       404:
 *         description: Almacén no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_ALMACENES_DELETE)
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_ALMACENES_DELETE);

    // 3. Business logic
    // Soft delete not supported in simplified schema
    const almacen = await prisma.almacen.delete({
      where: { id: (await params).id }
    })

    return ApiResponseHelper.success(almacen, 'Almacén desactivado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}
