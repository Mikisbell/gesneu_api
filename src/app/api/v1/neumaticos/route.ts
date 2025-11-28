import { NextRequest } from 'next/server'
import { NeumaticoService } from '@/lib/services/neumatico.service'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { CreateNeumaticoDTO } from '@/types/domain/neumatico.types'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

const service = new NeumaticoService()

/**
 * @swagger
 * /api/v1/neumaticos:
 *   get:
 *     summary: Listar neumáticos
 *     description: Obtiene una lista paginada de neumáticos con opciones de filtrado.
 *     tags: [Neumáticos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: numero_serie
 *         schema:
 *           type: string
 *         description: Filtrar por número de serie
 *       - in: query
 *         name: modelo_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Filtrar por ID de modelo
 *       - in: query
 *         name: estado_actual
 *         schema:
 *           type: string
 *           enum: [STOCK, MONTADO, REPARACION, REENCAUCHE, DESECHO]
 *         description: Filtrar por estado actual
 *       - in: query
 *         name: ubicacion_almacen_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Filtrar por ubicación en almacén
 *       - in: query
 *         name: ubicacion_vehiculo_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Filtrar por ubicación en vehículo
 *       - in: query
 *         name: activo
 *         schema:
 *           type: boolean
 *         description: Filtrar por estado activo/inactivo
 *     responses:
 *       200:
 *         description: Lista de neumáticos recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/Neumatico'
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_READ)
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        // 3. Business logic
        const { searchParams } = new URL(request.url)
        const filters = {
            numero_serie: searchParams.get('numero_serie') || undefined,
            modelo_id: searchParams.get('modelo_id') || undefined,
            estado_actual: searchParams.get('estado_actual') as any || undefined,
            ubicacion_almacen_id: searchParams.get('ubicacion_almacen_id') || undefined,
            ubicacion_vehiculo_id: searchParams.get('ubicacion_vehiculo_id') || undefined,
            dot: searchParams.get('dot') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined
        }

        const neumaticos = await service.getAll(filters)
        return ApiResponseHelper.success(neumaticos)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

/**
 * @swagger
 * /api/v1/neumaticos:
 *   post:
 *     summary: Crear neumático
 *     description: Crea un nuevo neumático en el sistema.
 *     tags: [Neumáticos]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateNeumaticoDTO'
 *     responses:
 *       201:
 *         description: Neumático creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Neumatico'
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_CREATE)
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_CREATE);

        // 3. Business logic
        const body = await request.json() as CreateNeumaticoDTO
        const neumatico = await service.create(body)
        return ApiResponseHelper.created(neumatico, 'Neumático creado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
