import { prisma } from '@/lib/prisma';
import { TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';
import { EmailService } from './email.service';

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
     * Crea alerta CRITICAL para neumáticos con profundidad_remanente_actual_mm < 4
     */
    async generarAlertasProfundidad(): Promise<number> {
        const PROFUNDIDAD_MINIMA = 4;

        // Buscar neumáticos críticos sin alerta activa
        const neumaticosCriticos = await prisma.neumatico.findMany({
            where: {
                profundidad_remanente_actual_mm: { lt: PROFUNDIDAD_MINIMA },
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
        const alertasCreadas: any[] = [];

        for (const n of neumaticosCriticos) {
            const alerta = await prisma.alerta.create({
                data: {
                    tipo: TipoAlertaEnum.PROFUNDIDAD_MINIMA,
                    severidad: SeveridadAlertaEnum.CRITICAL,
                    neumatico_id: n.id,
                    vehiculo_id: n.ubicacion_vehiculo_id,
                    mensaje: `Neumático ${n.numero_serie} tiene profundidad ${n.profundidad_remanente_actual_mm?.toFixed(1)}mm (mínimo: ${PROFUNDIDAD_MINIMA}mm)`
                }
            });
            alertasCreadas.push({
                ...alerta,
                neumatico: n,
                vehiculo: n.ubicacion_vehiculo
            });
            count++;
        }

        // Enviar emails para alertas críticas
        if (alertasCreadas.length > 0) {
            await this.enviarNotificacionesEmail(alertasCreadas);
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
     * Genera alerta de presión baja.
     * Se llama desde InspeccionService cuando presión < umbral mínimo.
     */
    async generarAlertaPresion(
        neumaticoId: string,
        presionActual: number,
        presionMinima: number = 80 // PSI mínimo por defecto
    ): Promise<boolean> {
        // Solo generar si presión está por debajo del umbral
        if (presionActual >= presionMinima) return false;

        // Obtener datos del neumático
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumaticoId },
            select: {
                numero_serie: true,
                ubicacion_vehiculo_id: true,
                ubicacion_vehiculo: { select: { placa: true } }
            }
        });

        if (!neumatico) return false;

        // Verificar si ya existe alerta no resuelta para este neumático
        const alertaExistente = await prisma.alerta.findFirst({
            where: {
                neumatico_id: neumaticoId,
                tipo: TipoAlertaEnum.PRESION_BAJA,
                resuelta: false
            }
        });

        if (alertaExistente) return false; // Ya tiene alerta activa

        // Determinar severidad
        const severidad = presionActual < (presionMinima * 0.7)
            ? SeveridadAlertaEnum.CRITICAL
            : SeveridadAlertaEnum.WARNING;

        // Crear alerta
        const alerta = await prisma.alerta.create({
            data: {
                tipo: TipoAlertaEnum.PRESION_BAJA,
                severidad,
                neumatico_id: neumaticoId,
                vehiculo_id: neumatico.ubicacion_vehiculo_id,
                mensaje: `Neumático ${neumatico.numero_serie} tiene presión ${presionActual.toFixed(1)} PSI (mínimo: ${presionMinima} PSI)`
            }
        });

        const alertData = {
            ...alerta,
            neumatico: { numero_serie: neumatico.numero_serie },
            vehiculo: neumatico.ubicacion_vehiculo
        };

        // Enviar email si es crítica
        if (severidad === SeveridadAlertaEnum.CRITICAL) {
            await this.enviarNotificacionesEmail([alertData]);

            // WEBHOOK TRIGGER
            const webhookService = new (require('./webhook.service').WebhookService)();
            await webhookService.dispatch('ALERTA_CRITICAL', alertData);
        }

        return true;
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

    /**
     * Envía notificaciones por email para alertas críticas
     */
    private async enviarNotificacionesEmail(alertas: any[]): Promise<void> {
        // Obtener usuarios con rol ADMIN o GESTOR
        const destinatarios = await prisma.usuario.findMany({
            where: {
                activo: true,
                rol: { in: ['ADMIN', 'GESTOR'] },
                NOT: { email: '' }
            },
            select: { email: true, nombre_completo: true }
        });

        if (destinatarios.length === 0) {
            console.log('[AlertasService] No hay destinatarios para emails');
            return;
        }

        const recipients = destinatarios.map(d => ({
            email: d.email!,
            nombre: d.nombre_completo || undefined
        }));

        // Enviar un email por cada alerta crítica
        for (const alerta of alertas) {
            if (alerta.severidad !== SeveridadAlertaEnum.CRITICAL) continue;

            try {
                await EmailService.sendAlertNotification(recipients, {
                    tipo: alerta.tipo,
                    severidad: 'CRITICA',
                    mensaje: alerta.mensaje,
                    neumatico: alerta.neumatico ? {
                        numero_serie: alerta.neumatico.numero_serie,
                        profundidad_mm: alerta.neumatico.profundidad_remanente_actual_mm
                    } : undefined,
                    vehiculo: alerta.vehiculo ? {
                        placa: alerta.vehiculo.placa
                    } : undefined
                });
            } catch (error) {
                console.error('[AlertasService] Error enviando email:', error);
                // No fallar si el email no se puede enviar
            }
        }
    }
}
