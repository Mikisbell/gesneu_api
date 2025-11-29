import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

/**
 * @swagger
 * /api/v1/catalogos/proveedores:
 *   get:
 *     summary: Listar proveedores
 *     description: Obtiene una lista paginada de proveedores activos.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: Número de página
 *       - in: query
 *         name: pageSize
 *         schema:
 *           type: integer
 *           default: 10
 *         description: Cantidad de elementos por página
 *     responses:
 *       200:
 *         description: Lista de proveedores recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Proveedor'
 *                 meta:
 *                   type: object
 *                   properties:
 *                     page:
 *                       type: integer
 *                     limit:
 *                       type: integer
 *                     total:
 *                       type: integer
 *                     totalPages:
 *                       type: integer
 *                     hasNext:
 *                       type: boolean
 *                     hasPrev:
 *                       type: boolean
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_PROVEEDORES_READ)
 */
export async function GET(request: NextRequest) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_PROVEEDORES_READ);

    // 3. Business logic
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const pageSize = parseInt(searchParams.get('pageSize') || '10')
    const skip = (page - 1) * pageSize

    const [proveedores, total] = await Promise.all([
      prisma.proveedor.findMany({
        orderBy: { nombre: 'asc' },
        skip,
        take: pageSize
      }),
      prisma.proveedor.count()
    ])

    return ApiResponseHelper.paginated(proveedores, {
      page,
      limit: pageSize,
      total,
      totalPages: Math.ceil(total / pageSize),
      hasNext: page < Math.ceil(total / pageSize),
      hasPrev: page > 1
    })
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}

/**
 * @swagger
 * /api/v1/catalogos/proveedores:
 *   post:
 *     summary: Crear proveedor
 *     description: Crea un nuevo proveedor en el sistema.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateProveedorDTO'
 *     responses:
 *       201:
 *         description: Proveedor creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Proveedor'
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       409:
 *         description: RUC duplicado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere CATALOGOS_PROVEEDORES_CREATE)
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Authentication
    const session = await requireAuth();

    // 2. Authorization
    requirePermission(session, PERMISSIONS.CATALOGOS_PROVEEDORES_CREATE);

    // 3. Business logic
    const body = await request.json()

    // Validar campos requeridos
    if (!body.nombre || !body.tipo) {
      return ApiResponseHelper.error('Nombre y tipo son requeridos', 400)
    }

    // Verificar RUC único si existe
    if (body.ruc) {
      const existe = await prisma.proveedor.findUnique({
        where: { ruc: body.ruc }
      })
      if (existe) {
        return ApiResponseHelper.error('El RUC ya está registrado', 409)
      }
    }

    const proveedor = await prisma.proveedor.create({
      data: {
        tipo: body.tipo,
        nombre: body.nombre,
        ruc: body.ruc
      }
    })

    return ApiResponseHelper.created(proveedor, 'Proveedor creado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}
