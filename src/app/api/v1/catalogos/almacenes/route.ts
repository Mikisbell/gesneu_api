import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

/**
 * @swagger
 * /api/v1/catalogos/almacenes:
 *   get:
 *     summary: Listar almacenes
 *     description: Obtiene una lista de todos los almacenes activos.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de almacenes recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Almacen'
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_ALMACENES_READ)
 */
export async function GET(request: NextRequest) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_ALMACENES_READ);

    // 3. Business logic
    const almacenes = await prisma.almacen.findMany({
      where: {
        activo: true
      },
      orderBy: {
        nombre: 'asc'
      }
    })

    return ApiResponseHelper.success(almacenes)
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}

/**
 * @swagger
 * /api/v1/catalogos/almacenes:
 *   post:
 *     summary: Crear almacén
 *     description: Crea un nuevo almacén en el sistema.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateAlmacenDTO'
 *     responses:
 *       201:
 *         description: Almacén creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Almacen'
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       409:
 *         description: Código de almacén duplicado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_ALMACENES_CREATE)
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_ALMACENES_CREATE);

    // 3. Business logic
    const body = await request.json()

    // Validar campos requeridos
    if (!body.nombre || !body.codigo) {
      return ApiResponseHelper.error('Nombre y código son requeridos', 400)
    }

    // Verificar código único
    const existe = await prisma.almacen.findUnique({
      where: { codigo: body.codigo }
    })

    if (existe) {
      return ApiResponseHelper.error('El código de almacén ya existe', 409)
    }

    const almacen = await prisma.almacen.create({
      data: {
        nombre: body.nombre,
        codigo: body.codigo,
        descripcion: body.descripcion,
        ubicacion: body.ubicacion,
        activo: body.activo ?? true
      }
    })

    return ApiResponseHelper.created(almacen, 'Almacén creado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}
