import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { MontajeNeumaticoSchema, type MontajeNeumaticoInput } from '@/lib/validators/montaje';

/**
 * @swagger
 * /api/v1/operaciones/montaje:
 *   post:
 *     summary: Montar un neumático en un vehículo
 *     description: Registra la instalación de un neumático en una posición específica de un vehículo.
 *     tags:
 *       - Operaciones
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - neumatico_id
 *               - vehiculo_id
 *               - contador_vehiculo
 *               - profundidad_mm
 *               - presion_psi
 *             properties:
 *               neumatico_id:
 *                 type: string
 *                 format: uuid
 *                 description: ID del neumático a montar
 *               vehiculo_id:
 *                 type: string
 *                 format: uuid
 *                 description: ID del vehículo destino
 *               posicion_neumatico_id:
 *                 type: string
 *                 format: uuid
 *                 description: ID de la posición en el vehículo (opcional si es repuesto)
 *               contador_vehiculo:
 *                 type: number
 *                 description: Kilometraje u horas del vehículo al momento del montaje
 *               profundidad_mm:
 *                 type: number
 *                 description: Profundidad de diseño o remanente actual (mm)
 *               presion_psi:
 *                 type: number
 *                 description: Presión de inflado (PSI)
 *               observaciones:
 *                 type: string
 *     responses:
 *       200:
 *         description: Montaje realizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     evento:
 *                       type: object
 *                       properties:
 *                         id:
 *                           type: string
 *                           format: uuid
 *                         tipo_evento:
 *                           type: string
 *                           example: "INSTALACION"
 *                     neumatico:
 *                       type: object
 *                       properties:
 *                         id:
 *                           type: string
 *                           format: uuid
 *                         estado_actual:
 *                           type: string
 *                           example: "INSTALADO"
 *       400:
 *         description: Datos inválidos
 *       404:
 *         description: Neumático o vehículo no encontrado
 *       409:
 *         description: El neumático no está en stock (ya montado o desechado)
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación y autorización
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION);

        // 2. Validar entrada
        const body = await request.json();
        const validatedData = MontajeNeumaticoSchema.parse(body);

        // 3. Validaciones de negocio
        const { neumatico } = await validateMontaje(validatedData);

        // 4. Ejecutar montaje en transacción
        const resultado = await ejecutarMontaje(validatedData, session.user.id, neumatico);

        return ApiResponseHelper.success(resultado, 'Neumático montado exitosamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * Validaciones de negocio antes del montaje
 */
async function validateMontaje(data: MontajeNeumaticoInput) {
    // 1. Verificar que el neumático existe
    const neumatico = await prisma.neumatico.findUnique({
        where: { id: data.neumatico_id },
        include: { modelo: true },
    });

    if (!neumatico) {
        throw new Error('Neumático no encontrado');
    }

    // 2. Verificar que el neumático está EN_STOCK
    if (neumatico.estado_actual !== 'EN_STOCK') {
        throw new Error(`Neumático no está disponible. Estado actual: ${neumatico.estado_actual}`);
    }

    // 3. Verificar que el vehículo existe
    const vehiculo = await prisma.vehiculo.findUnique({
        where: { id: data.vehiculo_id },
        include: { tipo_vehiculo: true },
    });

    if (!vehiculo) {
        throw new Error('Vehículo no encontrado');
    }

    // 4. NUEVO: Validar política de reencauchados por posición
    if (data.posicion_neumatico_id && neumatico.es_reencauchado) {
        const posicion = await prisma.posicionNeumatico.findUnique({
            where: { id: data.posicion_neumatico_id },
            include: { configuracion_eje: true }
        });

        if (posicion) {
            // Verificar restricción a nivel de posición
            if (!posicion.permite_reencauchado) {
                throw new Error(`Posición ${posicion.numero_posicion} (${posicion.lado_vehiculo}) no permite neumáticos reencauchados`);
            }

            // Verificar restricción a nivel de eje (ConfiguracionEje)
            if (!posicion.configuracion_eje.permite_reencauchados) {
                throw new Error(`Eje ${posicion.configuracion_eje.tipo_eje} no permite neumáticos reencauchados`);
            }
        }
    }

    return { neumatico, vehiculo };
}

/**
 * Ejecuta el montaje en una transacción atómica
 */
async function ejecutarMontaje(data: MontajeNeumaticoInput, usuario_id: string, neumatico: any) {
    return await prisma.$transaction(async (tx) => {
        const now = new Date();

        // 1. Crear evento de instalación
        const evento = await tx.eventoNeumatico.create({
            data: {
                tipo_evento: 'INSTALACION',
                neumatico_id: data.neumatico_id,
                fecha_evento: now,
                contador_vehiculo: data.contador_vehiculo,
                profundidad_remanente: data.profundidad_mm,
                presion_psi: data.presion_psi,
                vehiculo_id: data.vehiculo_id,
                posicion_montaje_id: data.posicion_neumatico_id,
                notas: data.observaciones,
                creado_por: usuario_id,
            },
        });

        // 2. Actualizar neumático
        const neumaticoActualizado = await tx.neumatico.update({
            where: { id: data.neumatico_id },
            data: {
                estado_actual: 'INSTALADO',
                ubicacion_almacen_id: null,
                ubicacion_vehiculo_id: data.vehiculo_id,
                ubicacion_posicion_id: data.posicion_neumatico_id || null
            },
        });

        return {
            evento: {
                id: evento.id,
                tipo_evento: evento.tipo_evento,
                neumatico_id: evento.neumatico_id,
                vehiculo_id: evento.vehiculo_id,
                fecha_evento: evento.fecha_evento,
            },
            neumatico: {
                id: neumaticoActualizado.id,
                numero_serie: neumaticoActualizado.numero_serie,
                estado_actual: neumaticoActualizado.estado_actual,
                ubicacion_vehiculo_id: neumaticoActualizado.ubicacion_vehiculo_id,
            },
        };
    });
}
