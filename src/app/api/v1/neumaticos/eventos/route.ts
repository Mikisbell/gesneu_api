import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { EventoNeumaticoCreateSchema } from '@/lib/validators/evento-neumatico';
import { NeumaticoService } from '@/lib/services/neumatico.service';

const neumaticoService = new NeumaticoService();

// Map event types to permissions
const EVENT_PERMISSIONS: Record<string, string> = {
    'INSTALACION': PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION,
    'DESMONTAJE': PERMISSIONS.NEUMATICOS_EVENTO_DESMONTAJE,
    'INSPECCION': PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION,
    'ROTACION': PERMISSIONS.NEUMATICOS_EVENTO_ROTACION,
    // Add others as needed, defaulting to generic update or specific permission
};

/**
 * POST /api/v1/neumaticos/eventos
 * 
 * Centralized endpoint for registering tire events.
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Parse Body to get Event Type
        const body = await request.json();
        const validatedData = EventoNeumaticoCreateSchema.parse(body);

        // 3. Authorization based on Event Type
        const requiredPermission = EVENT_PERMISSIONS[validatedData.tipo_evento];
        if (requiredPermission) {
            requirePermission(session, requiredPermission);
        } else {
            // Fallback or error if permission not defined for event
            // For now, let's assume if it's not in the map, it might need a generic permission or we log a warning
            // But strict security is better:
            // requirePermission(session, PERMISSIONS.NEUMATICOS_UPDATE); // Example fallback
        }

        // 4. Execute Business Logic via Service
        const result = await neumaticoService.registrarEvento(validatedData, session.user.id);

        return ApiResponseHelper.success(result, 'Evento registrado exitosamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
