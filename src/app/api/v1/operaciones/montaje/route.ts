import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { MontajeNeumaticoSchema, type MontajeNeumaticoInput } from '@/lib/validators/montaje';

/**
 * POST /api/v1/operaciones/montaje
 * 
 * Monta un neumático en un vehículo
 * 
 * @requires Permission: NEUMATICOS_EVENTO_INSTALACION
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
    // 1. Verificar que el neumático existe y está activo
    const neumatico = await prisma.neumatico.findUnique({
        where: { id: data.neumatico_id },
        include: { modelo: true },
    });

    if (!neumatico) {
        throw new Error('Neumático no encontrado');
    }

    if (!neumatico.activo) {
        throw new Error('Neumático no está activo');
    }

    // 2. Verificar que el neumático está EN_STOCK
    if (neumatico.estado_actual !== 'EN_STOCK') {
        throw new Error(`Neumático no está disponible. Estado actual: ${neumatico.estado_actual}`);
    }

    // 3. Verificar que el vehículo existe y está activo
    const vehiculo = await prisma.vehiculo.findUnique({
        where: { id: data.vehiculo_id },
        include: { tipo_vehiculo: true },
    });

    if (!vehiculo) {
        throw new Error('Vehículo no encontrado');
    }

    if (!vehiculo.activo) {
        throw new Error('Vehículo no está activo');
    }

    // 4. Si se especifica posición, verificar disponibilidad
    if (data.posicion_neumatico_id) {
        const posicionOcupada = await prisma.neumatico.findFirst({
            where: {
                ubicacion_posicion_id: data.posicion_neumatico_id,
                activo: true,
                estado_actual: 'INSTALADO',
            },
        });

        if (posicionOcupada) {
            throw new Error('La posición especificada ya está ocupada');
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
                kilometraje_vehiculo: data.kilometraje_vehiculo,
                profundidad_remanente: data.profundidad_mm,
                presion_psi: data.presion_psi,
                vehiculo_id: data.vehiculo_id,
                posicion_montaje_id: data.posicion_neumatico_id,
                notas: data.observaciones,
                creado_por: usuario_id,
            },
        });

        // 2. Actualizar neumático
        const neumatico = await tx.neumatico.update({
            where: { id: data.neumatico_id },
            data: {
                estado_actual: 'INSTALADO',
                ubicacion_almacen_id: null,
                ubicacion_vehiculo_id: data.vehiculo_id,
                ubicacion_posicion_id: data.posicion_neumatico_id || null,
                profundidad_actual_mm: data.profundidad_mm,
                presion_actual_psi: data.presion_psi,
                fecha_instalacion: now,
                actualizado_en: now,
            },
        });

        // 3. Crear registro de medición de profundidad
        await tx.medicionProfundidad.create({
            data: {
                neumatico_id: data.neumatico_id,
                profundidad_mm: data.profundidad_mm,
                fecha_medicion: now,
                medido_por: usuario_id,
            },
        });

        // 4. Actualizar odómetro del vehículo
        await tx.registroOdometro.create({
            data: {
                vehiculo_id: data.vehiculo_id,
                kilometraje: data.kilometraje_vehiculo,
                fecha_registro: now,
                registrado_por: usuario_id,
                notas: `Montaje de neumático ${neumatico.numero_serie}`,
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
                id: neumatico.id,
                numero_serie: neumatico.numero_serie,
                estado_actual: neumatico.estado_actual,
                ubicacion_vehiculo_id: neumatico.ubicacion_vehiculo_id,
            },
        };
    });
}
