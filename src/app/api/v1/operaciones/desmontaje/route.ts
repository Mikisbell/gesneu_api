import { NextRequest } from 'next/server';
import { OperacionesNeumaticosService } from '@/lib/services/operaciones-neumaticos.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { DesmontajeNeumaticoDTO } from '@/types/domain/operaciones.types';

const service = new OperacionesNeumaticosService();

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Validación básica
        if (!body.neumatico_id || !body.destino) {
            throw new Error('Faltan campos requeridos: neumatico_id, destino');
        }

        const data: DesmontajeNeumaticoDTO = {
            neumatico_id: body.neumatico_id,
            destino: body.destino,
            kilometraje_vehiculo: Number(body.kilometraje_vehiculo || 0),
            almacen_destino_id: body.almacen_destino_id,
            motivo_id: body.motivo_id,
            profundidad_remanente_mm: body.profundidad_remanente_mm ? Number(body.profundidad_remanente_mm) : undefined,
            presion_psi: body.presion_psi ? Number(body.presion_psi) : undefined,
            observaciones: body.observaciones,
            fecha_evento: body.fecha_evento ? new Date(body.fecha_evento) : undefined
        };

        const resultado = await service.desmontarNeumatico(data);

        return ApiResponseHelper.success(resultado, 'Neumático desmontado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
