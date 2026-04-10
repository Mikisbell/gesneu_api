import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rutaService } from '@/lib/services/ruta.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateRutaSchema } from '@/lib/validators/ruta.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/rutas:
 *   get:
 *     summary: Listar rutas
 *     description: Retorna todas las rutas, con filtros opcionales
 *     tags: [Rutas]
 *     parameters:
 *       - name: activo
 *         in: query
 *         description: Filtrar por estado activo
 *         schema:
 *           type: boolean
 *       - name: tipo_ruta_id
 *         in: query
 *         description: Filtrar por tipo de ruta
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Lista de rutas obtenida exitosamente
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        const filters = {
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
            tipo_ruta_id: searchParams.get('tipo_ruta_id') || undefined,
        };

        const result = await rutaService.getAll(session.user.empresa_id, filters);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

/**
 * @swagger
 * /api/v1/rutas:
 *   post:
 *     summary: Crear una nueva ruta
 *     description: Registra una ruta con origen, destino, distancia y tipo
 *     tags: [Rutas]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [nombre, tipo_ruta_id]
 *             properties:
 *               nombre:
 *                 type: string
 *                 maxLength: 100
 *               origen:
 *                 type: string
 *                 maxLength: 100
 *               destino:
 *                 type: string
 *                 maxLength: 100
 *               distancia_km:
 *                 type: number
 *                 minimum: 0
 *               tipo_ruta_id:
 *                 type: string
 *                 format: uuid
 *               activo:
 *                 type: boolean
 *     responses:
 *       201:
 *         description: Ruta creada exitosamente
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await rutaService.create(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Ruta creada exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_CREATE,
        schema: CreateRutaSchema,
    }
);
