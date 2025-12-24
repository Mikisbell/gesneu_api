import { prisma } from '@/lib/prisma';
import { TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';

export interface AlertaFilters {
    tipo?: TipoAlertaEnum;
    severidad?: SeveridadAlertaEnum;
    leida?: boolean;
    resuelta?: boolean;
    limit?: number;
}

export interface GenerarAlertasResult {
    profundidad: number;
    reencauche: number;
    total: number;
}

export class AlertasService {
    /**
     * Obtiene alertas con filtros opcionales
     */
    async getAlertas(filters: AlertaFilters = {}) {
        const { tipo, severidad, leida, resuelta, limit = 50 } = filters;

        const where: any = {};
        if (tipo) where.tipo = tipo;
        if (severidad) where.severidad = severidad;
        if (leida !== undefined) where.leida = leida;
        if (resuelta !== undefined) where.resuelta = resuelta;

        return prisma.alerta.findMany({
            where,
            include: {
                neumatico: {
                    select: { id: true, numero_serie: true }
                },
                vehiculo: {
                    select: { id: true, placa: true, codigo_interno: true }
                }
            },
            orderBy: [
                { severidad: 'desc' }, // CRITICAL primero
                { creada_en: 'desc' }
            ],
            take: limit
        });
    }

    /**
     * Genera alertas de profundidad mínima.
     * Crea alerta CRITICAL para neumáticos con profundidad_actual_mm < 4
     */
    async generarAlertasProfundidad(): Promise<number> {
        const PROFUNDIDAD_MINIMA = 4;

        // Buscar neumáticos críticos sin alerta activa
        const neumaticosCriticos = await prisma.neumatico.findMany({
            where: {
                profundidad_actual_mm: { lt: PROFUNDIDAD_MINIMA },
                activo: true,
                estado_actual: { not: 'DESECHADO' },
                // Evitar duplicados: no crear si ya existe alerta no resuelta
                alertas: {
                    none: {
                        tipo: TipoAlertaEnum.PROFUNDIDAD_MINIMA,
                        resuelta: false
                    }
                }
            },
            include: {
                ubicacion_vehiculo: { select: { placa: true } }
            }
        });

        let count = 0;
        for (const n of neumaticosCriticos) {
            await prisma.alerta.create({
                data: {
                    tipo: TipoAlertaEnum.PROFUNDIDAD_MINIMA,
                    severidad: SeveridadAlertaEnum.CRITICAL,
                    neumatico_id: n.id,
                    vehiculo_id: n.ubicacion_vehiculo_id,
                    mensaje: `Neumático ${n.numero_serie} tiene profundidad ${n.profundidad_actual_mm?.toFixed(1)}mm (mínimo: ${PROFUNDIDAD_MINIMA}mm)`
                }
            });
            count++;
        }

        return count;
    }

    /**
     * Genera alertas de reencauche máximo.
     * Crea alerta WARNING cuando reencauches_realizados >= reencauches_maximos
     */
    async generarAlertasReencauche(): Promise<number> {
        // Buscar neumáticos que alcanzaron límite de reencauche
        const neumaticosLimite = await prisma.neumatico.findMany({
            where: {
                activo: true,
                estado_actual: { not: 'DESECHADO' },
                alertas: {
                    none: {
                        tipo: TipoAlertaEnum.REENCAUCHE_MAXIMO,
                        resuelta: false
                    }
                }
            },
            include: {
                modelo: { select: { reencauches_maximos: true } },
                ubicacion_vehiculo: { select: { placa: true } }
            }
        });

        let count = 0;
        for (const n of neumaticosLimite) {
            const maxReencauches = n.modelo.reencauches_maximos || 0;
            if (n.reencauches_realizados >= maxReencauches && maxReencauches > 0) {
                await prisma.alerta.create({
                    data: {
                        tipo: TipoAlertaEnum.REENCAUCHE_MAXIMO,
                        severidad: SeveridadAlertaEnum.WARNING,
                        neumatico_id: n.id,
                        vehiculo_id: n.ubicacion_vehiculo_id,
                        mensaje: `Neumático ${n.numero_serie} alcanzó límite de reencauches (${n.reencauches_realizados}/${maxReencauches})`
                    }
                });
                count++;
            }
        }

        return count;
    }

    /**
     * Ejecuta todos los generadores de alertas
     */
    async generarTodasLasAlertas(): Promise<GenerarAlertasResult> {
        const profundidad = await this.generarAlertasProfundidad();
        const reencauche = await this.generarAlertasReencauche();

        return {
            profundidad,
            reencauche,
            total: profundidad + reencauche
        };
    }

    /**
     * Marca una alerta como leída
     */
    async marcarComoLeida(alertaId: string) {
        return prisma.alerta.update({
            where: { id: alertaId },
            data: { leida: true }
        });
    }

    /**
     * Marca una alerta como resuelta
     */
    async resolver(alertaId: string) {
        return prisma.alerta.update({
            where: { id: alertaId },
            data: { resuelta: true, leida: true }
        });
    }
}
