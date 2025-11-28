import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

// GET /api/v1/catalogos/proveedores/[id] - Obtener proveedor por ID
/**
 * @swagger
 * /api/v1/catalogos/proveedores/{id}:
 *   get:
 *     summary: Obtener proveedor por ID
 *     description: Obtiene los detalles de un proveedor específico.
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
 *         description: ID del proveedor
 *     responses:
 *       200:
 *         description: Detalles del proveedor
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Proveedor'
 *       404:
 *         description: Proveedor no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_PROVEEDORES_READ)
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_PROVEEDORES_READ);

    // 3. Business logic
    const proveedor = await prisma.proveedor.findUnique({
      where: { id: (await params).id }
    })

    if (!proveedor) {
      return ApiResponseHelper.notFound()
    }

    return ApiResponseHelper.success(proveedor)
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}

/**
 * @swagger
 * /api/v1/catalogos/proveedores/{id}:
 *   put:
 *     summary: Actualizar proveedor
 *     description: Actualiza los datos de un proveedor existente.
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
 *         description: ID del proveedor
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateProveedorDTO'
 *     responses:
 *       200:
 *         description: Proveedor actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Proveedor'
 *                 message:
 *                   type: string
 *       404:
 *         description: Proveedor no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_PROVEEDORES_UPDATE)
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_PROVEEDORES_UPDATE);

    // 3. Business logic
    const body = await request.json()

    // Verificar que existe
    const existe = await prisma.proveedor.findUnique({
      where: { id: (await params).id }
    })

    if (!existe) {
      return ApiResponseHelper.notFound()
    }

    const proveedor = await prisma.proveedor.update({
      where: { id: (await params).id },
      data: {
        tipo: body.tipo,
        nombre: body.nombre,
        ruc: body.ruc,
        contacto_principal: body.contacto_principal,
        telefono: body.telefono,
        email: body.email,
        direccion: body.direccion,
        activo: body.activo,
        actualizado_en: new Date()
      }
    })

    return ApiResponseHelper.success(proveedor, 'Proveedor actualizado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}

/**
 * @swagger
 * /api/v1/catalogos/proveedores/{id}:
 *   delete:
 *     summary: Eliminar proveedor
 *     description: Desactiva (soft delete) un proveedor del sistema.
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
 *         description: ID del proveedor
 *     responses:
 *       200:
 *         description: Proveedor desactivado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Proveedor'
 *                 message:
 *                   type: string
 *       404:
 *         description: Proveedor no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_PROVEEDORES_DELETE)
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_PROVEEDORES_DELETE);

    // 3. Business logic
    const proveedor = await prisma.proveedor.update({
      where: { id: (await params).id },
      data: {
        activo: false,
        actualizado_en: new Date()
      }
    })

    return ApiResponseHelper.success(proveedor, 'Proveedor desactivado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}
