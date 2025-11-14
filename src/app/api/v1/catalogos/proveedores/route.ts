import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { z } from 'zod'
import { PAGINATION } from '@/lib/utils/constants'

// GET /api/v1/catalogos/proveedores - Listar todos los proveedores
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || PAGINATION.DEFAULT_PAGE.toString())
    const limit = Math.min(parseInt(searchParams.get('limit') || PAGINATION.DEFAULT_LIMIT.toString()), PAGINATION.MAX_LIMIT)
    const activo = searchParams.get('activo')

    const skip = (page - 1) * limit

    // Construir filtros
    const where: any = {}
    if (activo !== null && activo !== undefined) {
      where.activo = activo === 'true'
    }

    // Obtener total de registros
    const total = await prisma.proveedor.count({ where })

    // Obtener proveedores paginados
    const proveedores = await prisma.proveedor.findMany({
      where,
      skip,
      take: limit,
      orderBy: {
        nombre: 'asc'
      }
    })

    const pagination = ApiResponseHelper.createPagination(page, limit, total)
    return ApiResponseHelper.paginated(proveedores, pagination)
  } catch (error) {
    console.error('Error al obtener proveedores:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al obtener proveedores'
    )
  }
}

// POST /api/v1/catalogos/proveedores - Crear nuevo proveedor
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validación con Zod
    const ProveedorCreateSchema = z.object({
      tipo: z.enum(['FABRICANTE', 'DISTRIBUIDOR', 'SERVICIO_REPARACION', 'SERVICIO_REENCAUCHE', 'OTRO']),
      nombre: z.string().min(1).max(200),
      ruc: z.string().max(20).optional(),
      contacto_principal: z.string().max(200).optional(),
      telefono: z.string().max(20).optional(),
      email: z.string().email().max(100).optional(),
      direccion: z.string().optional(),
      activo: z.boolean().optional()
    })

    const validatedData = ProveedorCreateSchema.parse(body)

    const proveedor = await prisma.proveedor.create({
      data: {
        ...validatedData,
        activo: validatedData.activo ?? true,
        creado_en: new Date()
      }
    })

    return ApiResponseHelper.created(proveedor, 'Proveedor creado exitosamente')
  } catch (error) {
    return ApiResponseHelper.handleError(error)
  }
}
