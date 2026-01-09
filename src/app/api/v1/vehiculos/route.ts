/**
 * Vehiculos API Routes - Lista y Creación
 * 
 * Implementa los endpoints GET (listado) y POST (creación) para vehículos.
 * Usa el patrón Result para manejo explícito de errores.
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { NextRequest } from 'next/server';
import { VehiculoService } from '@/lib/services/vehiculo.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import {
    validateCreateVehiculo,
    validateVehiculoFilters,
    formatZodErrors,
    getFirstZodError,
} from '@/lib/validators/vehiculo.validator';
import { isBusinessError } from '@/types/result.types';

const service = new VehiculoService();

/**
 * @swagger
 * /api/v1/vehiculos:
 *   get:
 *     summary: Listar vehículos
 *     description: Obtiene una lista paginada de vehículos con opciones de filtrado.
 *     tags: [Vehículos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: placa
 *         schema:
 *           type: string
 *         description: Filtrar por placa
 *       - in: query
 *         name: marca
 *         schema:
 *           type: string
 *         description: Filtrar por marca
 *       - in: query
 *         name: tipo_vehiculo_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Filtrar por tipo de vehículo
 *       - in: query
 *         name: activo
 *         schema:
 *           type: boolean
 *         description: Filtrar por estado activo/inactivo
 *     responses:
 *       200:
 *         description: Lista de vehículos recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Vehiculo'
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere VEHICULOS_READ)
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_READ);

        // 3. Parse filters
        const { searchParams } = new URL(request.url);
        const filters = {
            placa: searchParams.get('placa') || undefined,
            marca: searchParams.get('marca') || undefined,
            tipo_vehiculo_id: searchParams.get('tipo_vehiculo_id') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
        };

        // 4. Use legacy format for frontend backward compatibility
        // TODO: Migrate frontend to use new VehiculoResponse format, then use getAll()
        const vehiculos = await service.getAllLegacy(filters);

        return ApiResponseHelper.success(vehiculos);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/vehiculos:
 *   post:
 *     summary: Crear vehículo
 *     description: Crea un nuevo vehículo en el sistema.
 *     tags: [Vehículos]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateVehiculoDTO'
 *     responses:
 *       201:
 *         description: Vehículo creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Vehiculo'
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere VEHICULOS_CREATE)
 *       409:
 *         description: Conflicto (placa duplicada)
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_CREATE);

        // 3. Parse and validate body
        const body = await request.json();
        const validation = validateCreateVehiculo(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(
                formatZodErrors(validation.error),
                getFirstZodError(validation.error)
            );
        }

        // 4. Get empresa_id from session (multi-tenancy)
        const empresa_id = session.user.empresa_id;
        if (!empresa_id) {
            return ApiResponseHelper.error('Usuario no tiene empresa asignada', 403);
        }

        // 5. Business logic with Result handling
        const result = await service.create(validation.data as any, empresa_id);

        if (!result.success) {
            // Handle known business errors with appropriate status codes
            if (isBusinessError(result.error)) {
                return ApiResponseHelper.error(
                    result.error.message,
                    result.error.statusCode
                );
            }
            return ApiResponseHelper.error((result.error as Error).message || 'Error desconocido', 500);
        }

        return ApiResponseHelper.created(result.data, 'Vehículo creado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
