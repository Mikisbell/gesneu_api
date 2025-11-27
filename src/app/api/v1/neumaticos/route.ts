import { NextRequest } from 'next/server'
import { NeumaticoService } from '@/lib/services/neumatico.service'
import { ApiResponseHelper } from '@/lib/api-response'
import { CreateNeumaticoDTO } from '@/types/domain/neumatico.types'

const service = new NeumaticoService()

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url)
        const filters = {
            numero_serie: searchParams.get('numero_serie') || undefined,
            modelo_id: searchParams.get('modelo_id') || undefined,
            estado_actual: searchParams.get('estado_actual') as any || undefined,
            ubicacion_almacen_id: searchParams.get('ubicacion_almacen_id') || undefined,
            ubicacion_vehiculo_id: searchParams.get('ubicacion_vehiculo_id') || undefined,
            dot: searchParams.get('dot') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined
        }

        const neumaticos = await service.getAll(filters)
        return ApiResponseHelper.success(neumaticos)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json() as CreateNeumaticoDTO
        const neumatico = await service.create(body)
        return ApiResponseHelper.created(neumatico, 'Neumático creado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
