import { NextRequest } from 'next/server'
import { VehiculoService } from '@/lib/services/vehiculo.service'
import { ApiResponseHelper } from '@/lib/api-response'
import { UpdateVehiculoDTO } from '@/types/domain/vehiculo.types'

const service = new VehiculoService()

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const vehiculo = await service.getById((await params).id)
        if (!vehiculo) {
            return ApiResponseHelper.notFound('Vehículo no encontrado')
        }
        return ApiResponseHelper.success(vehiculo)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const body = await request.json() as UpdateVehiculoDTO
        const vehiculo = await service.update((await params).id, body)
        return ApiResponseHelper.success(vehiculo, 'Vehículo actualizado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

export async function DELETE(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const vehiculo = await service.delete((await params).id)
        return ApiResponseHelper.success(vehiculo, 'Vehículo eliminado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
