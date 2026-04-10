import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { parametroSistemaService } from '@/lib/services/parametro-sistema.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateParametroSistemaSchema } from '@/lib/validators/parametro-sistema.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/configuracion/parametros:
 *   get:
 *     summary: Obtener todos los parametros del sistema agrupados
 *     description: Retorna todos los parametros del sistema organizados por categoria
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Parametros del sistema agrupados por categoria
 *       401:
 *         description: No autorizado
 */
export const GET = apiHandler(
    async (req, session) => {
        const result = await parametroSistemaService.getAll();
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);

/**
 * @swagger
 * /api/v1/configuracion/parametros:
 *   post:
 *     summary: Crear parametro del sistema
 *     description: Crea un nuevo parametro de configuracion del sistema
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - clave
 *               - valor
 *             properties:
 *               clave:
 *                 type: string
 *                 maxLength: 100
 *                 description: "Clave unica del parametro (ej: EMPRESA_NOMBRE)"
 *               valor:
 *                 type: string
 *                 description: "Valor del parametro"
 *               tipo_dato:
 *                 type: string
 *                 enum: [STRING, NUMBER, BOOLEAN, JSON]
 *                 default: STRING
 *               categoria:
 *                 type: string
 *                 maxLength: 50
 *                 description: "Categoria para agrupacion (ej: GENERAL, ALERTAS, REPORTES)"
 *               descripcion:
 *                 type: string
 *                 maxLength: 1000
 *               valor_default:
 *                 type: string
 *               editable:
 *                 type: boolean
 *                 default: true
 *               requiere_reinicio:
 *                 type: boolean
 *                 default: false
 *     responses:
 *       201:
 *         description: Parametro del sistema creado exitosamente
 *       400:
 *         description: Error de validacion
 *       409:
 *         description: Ya existe un parametro con esta clave
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await parametroSistemaService.create(body, session.user.id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Parametro del sistema creado exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_AJUSTES_READ,
        schema: CreateParametroSistemaSchema
    }
);
