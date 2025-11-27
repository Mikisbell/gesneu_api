import { NextRequest } from 'next/server';
import { OperacionesNeumaticosService } from '@/lib/services/operaciones-neumaticos.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { RotacionNeumaticoDTO } from '@/types/domain/operaciones.types';

const service = new OperacionesNeumaticosService();

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Validación básica
        if (!body.vehiculo_id || !body.movimientos || !Array.isArray(body.movimientos)) {
            throw new Error('Faltan campos requeridos: vehiculo_id, movimientos (array)');
        }

        const data: RotacionNeumaticoDTO = {
            vehiculo_id: body.vehiculo_id,
            kilometraje_vehiculo: Number(body.kilometraje_vehiculo || 0),
            movimientos: body.movimientos.map((m: any) => ({
                neumatico_id: m.neumatico_id,
                posicion_destino_id: m.posicion_destino_id
            })),
            observaciones: body.observaciones
        };

        const resultado = await service.rotarNeumaticos(data);

        return ApiResponseHelper.success(resultado, `${resultado.length} neumáticos rotados exitosamente`);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
