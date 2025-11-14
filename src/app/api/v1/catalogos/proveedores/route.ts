import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'

// GET /api/v1/catalogos/proveedores - Listar todos los proveedores
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const pageSize = parseInt(searchParams.get('pageSize') || '10')
    const activo = searchParams.get('activo')

    const skip = (page - 1) * pageSize

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
      take: pageSize,
      orderBy: {
        nombre: 'asc'
      }
    })

    return ApiResponseHelper.paginated(proveedores, page, pageSize, total)
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

    // Validaciones básicas
    if (!body.nombre || !body.tipo) {
      return ApiResponseHelper.badRequest('Nombre y tipo son requeridos')
    }

    const proveedor = await prisma.proveedor.create({
      data: {
        tipo: body.tipo,
        nombre: body.nombre,
        ruc: body.ruc || null,
        contacto_principal: body.contacto_principal || null,
        telefono: body.telefono || null,
        email: body.email || null,
        direccion: body.direccion || null,
        activo: body.activo !== undefined ? body.activo : true
      }
    })

    return ApiResponseHelper.success(proveedor, 'Proveedor creado exitosamente')
  } catch (error) {
    console.error('Error al crear proveedor:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al crear proveedor'
    )
  }
}
