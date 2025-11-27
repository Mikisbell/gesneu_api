import { NextRequest } from 'next/server'
import { NeumaticoService } from '@/lib/services/neumatico.service'
import { ApiResponseHelper } from '@/lib/api-response'
import { UpdateNeumaticoDTO } from '@/types/domain/neumatico.types'

const service = new NeumaticoService()

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const neumatico = await service.getById(params.id)
        if (!neumatico) {
            return ApiResponseHelper.notFound('Neumático no encontrado')
        }
        return ApiResponseHelper.success(neumatico)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

export async function PUT(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const body = await request.json() as UpdateNeumaticoDTO
        const neumatico = await service.update(params.id, body)
        return ApiResponseHelper.success(neumatico, 'Neumático actualizado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

export async function DELETE(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const neumatico = await service.delete(params.id)
        return ApiResponseHelper.success(neumatico, 'Neumático eliminado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
