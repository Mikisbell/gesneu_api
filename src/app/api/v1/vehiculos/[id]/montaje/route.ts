import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { prisma } from '@/lib/prisma';

/**
 * @swagger
 * /api/v1/vehiculos/{id}/montaje:
 *   get:
 *     summary: Obtener mapa de montaje del vehículo
 *     description: Retorna la configuración de ejes y neumáticos montados con estado visual
 *     tags:
 *       - Vehículos
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Mapa de montaje del vehículo
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.VEHICULOS_READ);

        const { id } = await params;

        // Obtener vehículo con tipo y configuración
        const vehiculo = await prisma.vehiculo.findUnique({
            where: { id },
            include: {
                tipo_vehiculo: {
                    include: {
                        configuraciones: {
                            include: {
                                posiciones: {
                                    include: {
                                        neumaticos: {
                                            where: { estado_actual: 'INSTALADO' },
                                            include: { modelo: true }
                                        }
                                    },
                                    orderBy: [
                                        { lado_vehiculo: 'asc' },
                                        { numero_posicion: 'asc' }
                                    ]
                                }
                            },
                            orderBy: { numero_eje: 'asc' }
                        }
                    }
                }
            }
        });

        if (!vehiculo) {
            return ApiResponseHelper.notFound('Recurso no encontrado');
        }

        // Transformar datos para el componente visual
        const ejes = vehiculo.tipo_vehiculo?.configuraciones.map(eje => ({
            numero_eje: eje.numero_eje,
            tipo_eje: eje.tipo_eje,
            permite_reencauchados: eje.permite_reencauchados,
            posiciones: eje.posiciones.map(pos => {
                const neumatico = pos.neumaticos[0]; // Solo uno puede estar instalado

                // Calcular estado visual
                let estado: 'OK' | 'WARNING' | 'CRITICAL' | 'EMPTY' = 'EMPTY';
                let profundidadPorcentaje = 0;

                if (neumatico) {
                    const profInicial = neumatico.profundidad_inicial_mm || 18;
                    const profActual = neumatico.profundidad_actual_mm || 0;
                    profundidadPorcentaje = Math.round((profActual / profInicial) * 100);

                    if (profActual < 4) {
                        estado = 'CRITICAL';
                    } else if (profActual < 6) {
                        estado = 'WARNING';
                    } else {
                        estado = 'OK';
                    }
                }

                return {
                    id: pos.id,
                    numero_posicion: pos.numero_posicion,
                    lado: pos.lado_vehiculo,
                    permite_reencauchado: pos.permite_reencauchado,
                    estado,
                    neumatico: neumatico ? {
                        id: neumatico.id,
                        numero_serie: neumatico.numero_serie,
                        modelo: neumatico.modelo?.nombre || 'N/A',
                        medida: neumatico.modelo?.medida || 'N/A',
                        profundidad_mm: neumatico.profundidad_actual_mm,
                        profundidad_porcentaje: profundidadPorcentaje,
                        presion_psi: neumatico.presion_actual_psi,
                        es_reencauchado: neumatico.es_reencauchado,
                        km_acumulado: neumatico.kilometraje_acumulado
                    } : null
                };
            })
        })) || [];

        return ApiResponseHelper.success({
            vehiculo: {
                id: vehiculo.id,
                placa: vehiculo.placa,
                codigo_interno: vehiculo.codigo_interno,
                marca: vehiculo.marca,
                modelo: vehiculo.modelo,
                tipo: vehiculo.tipo_vehiculo?.nombre
            },
            ejes,
            resumen: {
                total_posiciones: ejes.reduce((acc, eje) => acc + eje.posiciones.length, 0),
                montados: ejes.reduce((acc, eje) => acc + eje.posiciones.filter(p => p.neumatico).length, 0),
                vacios: ejes.reduce((acc, eje) => acc + eje.posiciones.filter(p => !p.neumatico).length, 0),
                criticos: ejes.reduce((acc, eje) => acc + eje.posiciones.filter(p => p.estado === 'CRITICAL').length, 0),
                warnings: ejes.reduce((acc, eje) => acc + eje.posiciones.filter(p => p.estado === 'WARNING').length, 0)
            }
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
