import { NextRequest } from 'next/server'
import { VehiculoService } from '@/lib/services/vehiculo.service'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { CreateVehiculoDTO } from '@/types/domain/vehiculo.types'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

const service = new VehiculoService()

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

        // 3. Business logic
        const { searchParams } = new URL(request.url)
        const filters = {
            placa: searchParams.get('placa') || undefined,
            marca: searchParams.get('marca') || undefined,
            tipo_vehiculo_id: searchParams.get('tipo_vehiculo_id') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined
        }

        const vehiculos = await service.getAll(filters)
        return ApiResponseHelper.success(vehiculos)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
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
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_CREATE);

        // 3. Business logic
        const body = await request.json() as CreateVehiculoDTO
        const vehiculo = await service.create(body)
        return ApiResponseHelper.created(vehiculo, 'Vehículo creado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
