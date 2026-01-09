import { NextRequest } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import {
    validateCreateNeumatico,
    validateNeumaticoFilters,
    formatZodErrors
} from '@/lib/validators/neumatico.validator';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { asEmpresaId, asUsuarioId } from '@/types/branded.types';

const service = new NeumaticoService();

/**
 * @swagger
 * /api/v1/neumaticos:
 *   get:
 *     summary: Listar neumáticos
 *     description: Obtiene una lista paginada de neumáticos con opciones de filtrado.
 *     tags: [Neumáticos]
 *     security:
 *       - bearerAuth: []
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        // 3. Validation & Parsing
        const { searchParams } = new URL(request.url);
        const filtersRaw = {
            search: searchParams.get('q') || undefined,
            serie: searchParams.get('numero_serie') || undefined,
            marca: searchParams.get('marca') || undefined,
            estado: searchParams.get('estado') || undefined,
            vehiculo_id: searchParams.get('vehiculo_id') || undefined,
            ubicacion: searchParams.get('ubicacion') || undefined // ALMACEN assigned in Zod?
        };

        const validation = validateNeumaticoFilters(filtersRaw);
        if (!validation.success) {
            return ApiResponseHelper.validationError(formatZodErrors(validation.error));
        }

        // 4. Business Logic
        const result = await service.getAll(validation.data);

        if (!result.success) {
            return ApiResponseHelper.handleError(result.error);
        }

        return ApiResponseHelper.success(result.data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/neumaticos:
 *   post:
 *     summary: Crear neumático
 *     description: Crea un nuevo neumático en el sistema.
 *     tags: [Neumáticos]
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_CREATE);

        if (!session.user?.id) {
            return ApiResponseHelper.unauthorized();
        }

        // Ensure multi-tenancy
        const empresaId = session.user.empresa_id;
        if (!empresaId) {
            return ApiResponseHelper.forbidden('Usuario no asociado a una empresa');
        }

        // 3. Validation
        const json = await request.json();
        const validation = validateCreateNeumatico(json);

        if (!validation.success) {
            return ApiResponseHelper.validationError(formatZodErrors(validation.error));
        }

        // 4. Business logic
        const result = await service.create(
            validation.data,
            asEmpresaId(empresaId),
            asUsuarioId(session.user.id)
        );

        if (!result.success) {
            return ApiResponseHelper.handleError(result.error);
        }

        return ApiResponseHelper.created(result.data, 'Neumático creado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
