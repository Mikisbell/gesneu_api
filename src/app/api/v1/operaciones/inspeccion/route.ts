import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { InspeccionNeumaticoSchema } from '@/lib/validators/inspeccion';

export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación y autorización
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION);

        // 2. Validar entrada
        const body = await request.json();
        const validatedData = InspeccionNeumaticoSchema.parse(body);

        // 3. Validar existencia del neumático
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: validatedData.neumatico_id },
            include: { ubicacion_vehiculo: true }
        });

        if (!neumatico) {
            return ApiResponseHelper.notFound('Neumático no encontrado');
        }

        if (!neumatico.activo) {
            return ApiResponseHelper.error('El neumático no está activo', 400);
        }

        // 4. Ejecutar inspección en transacción
        const resultado = await prisma.$transaction(async (tx) => {
            // Registrar medición
            const medicion = await tx.medicionProfundidad.create({
                data: {
                    neumatico_id: neumatico.id,
                    profundidad_mm: validatedData.profundidad_mm,
                    fecha_medicion: new Date(),
                    medido_por: session.user.id,
                    notas: validatedData.observaciones,
                    posicion_medicion: neumatico.ubicacion_posicion ? 'CENTRO' : null, // Simplificado
                }
            });

            // Actualizar neumático
            const neumaticoActualizado = await tx.neumatico.update({
                where: { id: neumatico.id },
                data: {
                    profundidad_actual_mm: validatedData.profundidad_mm,
                    presion_actual_psi: validatedData.presion_psi,
                    // Si se provee kilometraje y está montado, actualizar acumulado (simplificado)
                }
            });

            // Registrar kilometraje si aplica
            if (validatedData.kilometraje_vehiculo && neumatico.vehiculo_id) {
                await tx.registroOdometro.create({
                    data: {
                        vehiculo_id: neumatico.vehiculo_id,
                        kilometraje: validatedData.kilometraje_vehiculo,
                        fecha_registro: new Date(),
                        registrado_por: session.user.id,
                        notas: `Inspección de neumático ${neumatico.numero_serie}`
                    }
                });
            }

            // Generar alerta si profundidad es crítica (< 3mm)
            let alerta = null;
            if (validatedData.profundidad_mm < 3) {
                alerta = await tx.alerta.create({
                    data: {
                        tipo_alerta: 'PROFUNDIDAD_CRITICA',
                        mensaje: `Neumático ${neumatico.numero_serie} con profundidad crítica: ${validatedData.profundidad_mm}mm`,
                        nivel_severidad: 'CRITICA',
                        estado_alerta: 'PENDIENTE',
                        neumatico_id: neumatico.id,
                        vehiculo_id: neumatico.vehiculo_id,
                        almacen_id: neumatico.ubicacion_almacen_id,
                    }
                });
            }

            return {
                medicion,
                neumatico: neumaticoActualizado,
                alerta
            };
        });

        return ApiResponseHelper.success({
            medicion: resultado.medicion,
            neumatico: resultado.neumatico,
            alerta: resultado.alerta ? {
                generada: true,
                tipo: resultado.alerta.nivel_severidad,
                mensaje: resultado.alerta.mensaje
            } : { generada: false }
        }, 'Inspección registrada exitosamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
