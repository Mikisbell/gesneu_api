import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { MontajeNeumaticoSchema } from '@/lib/validators/montaje';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

const service = new NeumaticoService();

/**
 * @swagger
 * /api/v1/operaciones/montaje:
 *   post:
 *     summary: Montar un neumático en un vehículo
 *     tags: [Operaciones]
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación y autorización
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION);

        // 2. Validar entrada
        const body = await request.json();
        const validatedData = MontajeNeumaticoSchema.parse(body);

        // 3. Preparar payload para el servicio
        // Mapeamos los campos del input (DTO Frontend) a los del dominio (Service/DB)
        const eventoPayload = {
            tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
            neumatico_id: validatedData.neumatico_id,
            vehiculo_id: validatedData.vehiculo_id,
            posicion_montaje_id: validatedData.posicion_neumatico_id,
            contador_vehiculo: validatedData.contador_vehiculo,
            profundidad_remanente: validatedData.profundidad_mm,
            presion_psi: validatedData.presion_psi,
            observaciones: validatedData.observaciones, // El servicio espera este campo para mapearlo a 'notas'
            fecha_evento: new Date().toISOString()
        };

        // 4. Ejecutar vía Servicio (Centraliza validación, transacción, historial y hooks)
        const resultado = await service.registrarEvento(eventoPayload, session.user.id);

        return ApiResponseHelper.success(resultado, 'Neumático montado exitosamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
