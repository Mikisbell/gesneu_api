import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { neumaticoService } from '@/lib/services/neumatico.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateNeumaticoSchema } from '@/lib/validators/neumatico.validator';
import { NeumaticoFilters } from '@/types/domain/neumatico.types';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { asEmpresaId, asUsuarioId } from '@/types/branded.types';

/**
 * @swagger
 * /api/v1/neumaticos:
 *   get:
 *     summary: Listar neumáticos
 *     tags: [Neumáticos]
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        // Parse basic filters
        const filters: NeumaticoFilters = {
            search: searchParams.get('q') || undefined,
            numero_serie: searchParams.get('numero_serie') || undefined,
            modelo_id: searchParams.get('modelo_id') || undefined,
            estado_actual: searchParams.get('estado') as any || undefined,
            ubicacion_vehiculo_id: searchParams.get('vehiculo_id') || undefined,
            ubicacion_almacen_id: searchParams.get('almacen_id') || undefined,
            dot: searchParams.get('dot') || undefined,
        };

        const result = await neumaticoService.getAll(session.user.empresa_id, filters);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);

/**
 * @swagger
 * /api/v1/neumaticos:
 *   post:
 *     summary: Crear neumático
 *     tags: [Neumáticos]
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        // Body is strictly typed by schema validation in apiHandler
        const result = await neumaticoService.create(
            body,
            session.user.empresa_id,
            session.user.id
        );

        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Neumático creado exitosamente');
    },
    {
        permission: PERMISSIONS.NEUMATICOS_CREATE,
        schema: CreateNeumaticoSchema
    }
);
