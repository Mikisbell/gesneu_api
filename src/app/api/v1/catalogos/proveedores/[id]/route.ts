import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'

// GET /api/v1/catalogos/proveedores/[id] - Obtener proveedor por ID
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const proveedor = await prisma.proveedor.findUnique({
      where: { id: params.id }
    })

    if (!proveedor) {
      return ApiResponseHelper.notFound('Proveedor no encontrado')
    }

    return ApiResponseHelper.success(proveedor)
  } catch (error) {
    console.error('Error al obtener proveedor:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al obtener proveedor'
    )
  }
}

// PUT /api/v1/catalogos/proveedores/[id] - Actualizar proveedor
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()

    // Verificar que existe
    const existe = await prisma.proveedor.findUnique({
      where: { id: params.id }
    })

    if (!existe) {
      return ApiResponseHelper.notFound('Proveedor no encontrado')
    }

    const proveedor = await prisma.proveedor.update({
      where: { id: params.id },
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
    console.error('Error al actualizar proveedor:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al actualizar proveedor'
    )
  }
}

// DELETE /api/v1/catalogos/proveedores/[id] - Eliminar proveedor (soft delete)
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const proveedor = await prisma.proveedor.update({
      where: { id: params.id },
      data: {
        activo: false,
        actualizado_en: new Date()
      }
    })

    return ApiResponseHelper.success(proveedor, 'Proveedor desactivado exitosamente')
  } catch (error) {
    console.error('Error al eliminar proveedor:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al eliminar proveedor'
    )
  }
}
