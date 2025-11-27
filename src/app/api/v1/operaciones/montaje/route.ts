import { NextRequest } from 'next/server';
import { OperacionesNeumaticosService } from '@/lib/services/operaciones-neumaticos.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { MontajeNeumaticoDTO } from '@/types/domain/operaciones.types';

const service = new OperacionesNeumaticosService();

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Validación básica
        if (!body.neumatico_id || !body.vehiculo_id || !body.posicion_id) {
            throw new Error('Faltan campos requeridos: neumatico_id, vehiculo_id, posicion_id');
        }

        const data: MontajeNeumaticoDTO = {
            neumatico_id: body.neumatico_id,
            vehiculo_id: body.vehiculo_id,
            posicion_id: body.posicion_id,
            kilometraje_vehiculo: Number(body.kilometraje_vehiculo || 0),
            presion_psi: body.presion_psi ? Number(body.presion_psi) : undefined,
            observaciones: body.observaciones,
            fecha_evento: body.fecha_evento ? new Date(body.fecha_evento) : undefined
        };

        const resultado = await service.montarNeumatico(data);

        return ApiResponseHelper.success(resultado, 'Neumático montado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
