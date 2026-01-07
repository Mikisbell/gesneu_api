import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { prisma } from '@/lib/prisma';
import { toNumber } from '@/lib/utils/decimal';
import { Prisma } from '@prisma/client';

// Type for the rich vehicle query result
type VehiculoWithMontaje = Prisma.VehiculoGetPayload<{
    include: {
        tipo_vehiculo: {
            include: {
                configuraciones: {
                    include: {
                        posiciones: {
                            include: {
                                neumaticos: {
                                    include: { modelo: true }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}>;

// Type for transformed position data
interface PosicionTransformada {
    id: string;
    numero_posicion: number;
    lado: string;
    permite_reencauchado: boolean;
    estado: 'OK' | 'WARNING' | 'CRITICAL' | 'EMPTY';
    neumatico: {
        id: string;
        numero_serie: string;
        modelo: string;
        medida: string;
        profundidad_mm: Prisma.Decimal;
        profundidad_porcentaje: number;
        presion_psi: Prisma.Decimal | null;
        es_reencauchado: boolean;
        km_acumulado: Prisma.Decimal;
    } | null;
}

// Type for transformed axle data
interface EjeTransformado {
    numero_eje: number;
    tipo_eje: string;
    permite_reencauchados: boolean;
    posiciones: PosicionTransformada[];
}

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
                                        { posicion_relativa: 'asc' }
                                    ]
                                }
                            },
                            orderBy: { numero_eje: 'asc' }
                        }
                    }
                }
            }
        }) as VehiculoWithMontaje | null;

        if (!vehiculo) {
            return ApiResponseHelper.notFound('Recurso no encontrado');
        }

        // Transformar datos para el componente visual
        const ejes: EjeTransformado[] = vehiculo.tipo_vehiculo?.configuraciones.map((eje) => ({
            numero_eje: eje.numero_eje,
            tipo_eje: eje.tipo_eje,
            permite_reencauchados: eje.permite_reencauchados,
            posiciones: eje.posiciones.map((pos): PosicionTransformada => {
                const neumatico = pos.neumaticos[0]; // Solo uno puede estar instalado

                // Calcular estado visual
                let estado: 'OK' | 'WARNING' | 'CRITICAL' | 'EMPTY' = 'EMPTY';
                let profundidadPorcentaje = 0;

                if (neumatico) {
                    const profInicial = toNumber(neumatico.profundidad_inicial_mm, 18);
                    const profActual = toNumber(neumatico.profundidad_remanente_actual_mm);
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
                    numero_posicion: pos.posicion_relativa,
                    lado: pos.lado,
                    permite_reencauchado: pos.permite_reencauchado,
                    estado,
                    neumatico: neumatico ? {
                        id: neumatico.id,
                        numero_serie: neumatico.numero_serie || 'S/N',
                        modelo: neumatico.modelo?.nombre_modelo || 'N/A',
                        medida: neumatico.modelo?.medida || 'N/A',
                        profundidad_mm: neumatico.profundidad_remanente_actual_mm,
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
                codigo_interno: vehiculo.numero_economico || vehiculo.placa,
                marca: vehiculo.marca,
                modelo: vehiculo.modelo_vehiculo,
                tipo: vehiculo.tipo_vehiculo?.nombre
            },
            ejes,
            resumen: {
                total_posiciones: ejes.reduce((acc: number, eje: EjeTransformado) => acc + eje.posiciones.length, 0),
                montados: ejes.reduce((acc: number, eje: EjeTransformado) => acc + eje.posiciones.filter((p: PosicionTransformada) => p.neumatico).length, 0),
                vacios: ejes.reduce((acc: number, eje: EjeTransformado) => acc + eje.posiciones.filter((p: PosicionTransformada) => !p.neumatico).length, 0),
                criticos: ejes.reduce((acc: number, eje: EjeTransformado) => acc + eje.posiciones.filter((p: PosicionTransformada) => p.estado === 'CRITICAL').length, 0),
                warnings: ejes.reduce((acc: number, eje: EjeTransformado) => acc + eje.posiciones.filter((p: PosicionTransformada) => p.estado === 'WARNING').length, 0)
            }
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
