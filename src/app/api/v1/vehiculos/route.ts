import { NextRequest } from 'next/server'
import { VehiculoService } from '@/lib/services/vehiculo.service'
import { ApiResponseHelper } from '@/lib/api-response'
import { CreateVehiculoDTO } from '@/types/domain/vehiculo.types'

const service = new VehiculoService()

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url)
        const filters = {
            placa: searchParams.get('placa') || undefined,
            marca: searchParams.get('marca') || undefined,
            tipo_vehiculo_id: searchParams.get('tipo_vehiculo_id') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined
        }

        const vehiculos = await service.getAll(filters)
        return ApiResponseHelper.success(vehiculos)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json() as CreateVehiculoDTO
        const vehiculo = await service.create(body)
        return ApiResponseHelper.created(vehiculo, 'Vehículo creado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
