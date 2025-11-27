import { NextResponse, NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'

export async function GET() {
  try {
    const almacenes = await prisma.almacen.findMany({
      where: {
        activo: true
      },
      orderBy: {
        nombre: 'asc'
      }
    })

    return NextResponse.json(almacenes)
  } catch (error) {
    console.error('Error fetching almacenes:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validar campos requeridos
    if (!body.nombre || !body.codigo) {
      return ApiResponseHelper.badRequest('Nombre y código son requeridos')
    }

    // Verificar código único
    const existe = await prisma.almacen.findUnique({
      where: { codigo: body.codigo }
    })

    if (existe) {
      return ApiResponseHelper.badRequest('El código de almacén ya existe')
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
    console.error('Error creating almacen:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al crear almacén'
    )
  }
}
