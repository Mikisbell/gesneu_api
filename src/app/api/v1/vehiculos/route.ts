import { NextRequest } from 'next/server';
import { VehiculoService } from '@/lib/services/vehiculo.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { CreateVehiculoDTO, VehiculoFilters } from '@/types/domain/vehiculo.types';

const service = new VehiculoService();

export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);

        const filters: VehiculoFilters = {
            placa: searchParams.get('placa') || undefined,
            tipo_vehiculo_id: searchParams.get('tipo_vehiculo_id') || undefined,
            marca: searchParams.get('marca') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
        };

        const vehiculos = await service.getAll(filters);

        return ApiResponseHelper.success(vehiculos);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        if (!body.placa || !body.tipo_vehiculo_id || !body.marca || !body.modelo) {
            throw new Error('Faltan campos requeridos: placa, tipo_vehiculo_id, marca, modelo');
        }

        const data: CreateVehiculoDTO = {
            placa: body.placa,
            tipo_vehiculo_id: body.tipo_vehiculo_id,
            marca: body.marca,
            modelo: body.modelo,
            anio: Number(body.anio_fabricacion),
            kilometraje_actual: Number(body.kilometraje_actual || 0),
            motor_serie: body.motor_serie,
            chasis_serie: body.chasis_serie,
            activo: body.activo ?? true,
        };

        const vehiculo = await service.create(data);

        return ApiResponseHelper.created(vehiculo, 'Vehículo creado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
