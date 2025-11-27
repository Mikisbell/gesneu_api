import { NextResponse, NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/api-response'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const pageSize = parseInt(searchParams.get('pageSize') || '10')
    const skip = (page - 1) * pageSize

    const [proveedores, total] = await Promise.all([
      prisma.proveedor.findMany({
        where: { activo: true },
        orderBy: { nombre: 'asc' },
        skip,
        take: pageSize
      }),
      prisma.proveedor.count({ where: { activo: true } })
    ])

    return NextResponse.json({
      data: proveedores,
      meta: {
        total,
        page,
        pageSize,
        totalPages: Math.ceil(total / pageSize)
      }
    })
  } catch (error) {
    console.error('Error fetching proveedores:', error)
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
    if (!body.nombre || !body.tipo) {
      return ApiResponseHelper.badRequest('Nombre y tipo son requeridos')
    }

    // Verificar RUC único si existe
    if (body.ruc) {
      const existe = await prisma.proveedor.findUnique({
        where: { ruc: body.ruc }
      })
      if (existe) {
        return ApiResponseHelper.badRequest('El RUC ya está registrado')
      }
    }

    const proveedor = await prisma.proveedor.create({
      data: {
        tipo: body.tipo,
        nombre: body.nombre,
        ruc: body.ruc,
        contacto_principal: body.contacto_principal,
        telefono: body.telefono,
        email: body.email,
        direccion: body.direccion,
        activo: body.activo ?? true
      }
    })

    return ApiResponseHelper.created(proveedor, 'Proveedor creado exitosamente')
  } catch (error) {
    console.error('Error creating proveedor:', error)
    return ApiResponseHelper.error(
      error instanceof Error ? error.message : 'Error al crear proveedor'
    )
  }
}
