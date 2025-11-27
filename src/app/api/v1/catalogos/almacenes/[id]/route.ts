import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'

// GET /api/v1/catalogos/almacenes/[id] - Obtener almacén por ID
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const almacen = await prisma.almacen.findUnique({
      where: { id: params.id }
    })

    if (!almacen) {
      return ApiResponseHelper.notFound('Almacén no encontrado')
    }

    return ApiResponseHelper.success(almacen)
  } catch (error) {
    console.error('Error al obtener almacén:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al obtener almacén'
    )
  }
}

// PUT /api/v1/catalogos/almacenes/[id] - Actualizar almacén
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()

    // Verificar que existe
    const existe = await prisma.almacen.findUnique({
      where: { id: params.id }
    })

    if (!existe) {
      return ApiResponseHelper.notFound('Almacén no encontrado')
    }

    const almacen = await prisma.almacen.update({
      where: { id: params.id },
      data: {
        nombre: body.nombre,
        ubicacion: body.ubicacion,
        activo: body.activo,
        actualizado_en: new Date()
      }
    })

    return ApiResponseHelper.success(almacen, 'Almacén actualizado exitosamente')
  } catch (error) {
    console.error('Error al actualizar almacén:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al actualizar almacén'
    )
  }
}

// DELETE /api/v1/catalogos/almacenes/[id] - Eliminar almacén (soft delete)
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const almacen = await prisma.almacen.update({
      where: { id: params.id },
      data: {
        activo: false,
        actualizado_en: new Date()
      }
    })

    return ApiResponseHelper.success(almacen, 'Almacén desactivado exitosamente')
  } catch (error) {
    console.error('Error al eliminar almacén:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al eliminar almacén'
    )
  }
}
