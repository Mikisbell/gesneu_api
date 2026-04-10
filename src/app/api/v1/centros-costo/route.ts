import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { centroCostoService } from '@/lib/services/centro-costo.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateCentroCostoSchema } from '@/lib/validators/centro-costo.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/centros-costo:
 *   get:
 *     summary: Listar centros de costo
 *     description: Retorna todos los centros de costo, con filtros opcionales
 *     tags: [Centros de Costo]
 *     parameters:
 *       - name: activo
 *         in: query
 *         description: Filtrar por estado activo
 *         schema:
 *           type: boolean
 *       - name: search
 *         in: query
 *         description: Buscar por nombre, código o área de negocio
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Lista de centros de costo obtenida exitosamente
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        const filters = {
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
            search: searchParams.get('search') || undefined,
        };

        const result = await centroCostoService.getAll(session.user.empresa_id, filters);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

/**
 * @swagger
 * /api/v1/centros-costo:
 *   post:
 *     summary: Crear un nuevo centro de costo
 *     description: Registra un centro de costo con código único, nombre y área de negocio
 *     tags: [Centros de Costo]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [codigo, nombre]
 *             properties:
 *               codigo:
 *                 type: string
 *                 maxLength: 20
 *               nombre:
 *                 type: string
 *                 maxLength: 100
 *               area_negocio:
 *                 type: string
 *                 maxLength: 100
 *               activo:
 *                 type: boolean
 *     responses:
 *       201:
 *         description: Centro de costo creado exitosamente
 *       409:
 *         description: Ya existe un centro de costo con este código
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        console.log('[CC POST] empresa_id:', session.user.empresa_id, 'userId:', session.user.id, 'body:', JSON.stringify(body));
        const result = await centroCostoService.create(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Centro de costo creado exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_CREATE,
        schema: CreateCentroCostoSchema,
    }
);
