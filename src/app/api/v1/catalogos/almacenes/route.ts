import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'

// GET /api/v1/catalogos/almacenes - Listar todos los almacenes
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
    const total = await prisma.almacen.count({ where })

    // Obtener almacenes paginados
    const almacenes = await prisma.almacen.findMany({
      where,
      skip,
      take: pageSize,
      orderBy: {
        nombre: 'asc'
      }
    })

    return ApiResponseHelper.paginated(almacenes, page, pageSize, total)
  } catch (error) {
    console.error('Error al obtener almacenes:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al obtener almacenes'
    )
  }
}

// POST /api/v1/catalogos/almacenes - Crear nuevo almacén
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validaciones básicas
    if (!body.nombre) {
      return ApiResponseHelper.badRequest('Nombre es requerido')
    }

    const almacen = await prisma.almacen.create({
      data: {
        nombre: body.nombre,
        tipo: body.tipo || null,
        ubicacion: body.ubicacion || null,
        responsable: body.responsable || null,
        activo: body.activo !== undefined ? body.activo : true
      }
    })

    return ApiResponseHelper.success(almacen, 'Almacén creado exitosamente')
  } catch (error) {
    console.error('Error al crear almacén:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al crear almacén'
    )
  }
}
