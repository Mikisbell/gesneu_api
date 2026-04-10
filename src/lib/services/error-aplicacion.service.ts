import { prisma } from '@/lib/prisma';
import {
    CreateErrorAplicacionInput,
    ResolveErrorInput
} from '@/lib/validators/error-aplicacion.validator';
import {
    Result,
    ok,
    err,
    BusinessError,
    NotFoundError
} from '@/types/result.types';
import { Prisma } from '@prisma/client';

/**
 * Serialize BigInt fields to strings for JSON compatibility
 */
function serializeBigInts<T>(obj: T): T {
    if (obj === null || obj === undefined) return obj;
    if (typeof obj === 'bigint') return obj.toString() as unknown as T;
    if (typeof obj === 'number') return obj;
    if (typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(serializeBigInts) as unknown as T;
    const result: any = {};
    for (const [key, value] of Object.entries(obj as object)) {
        result[key] = serializeBigInts(value);
    }
    return result;
}

export interface ErrorAplicacionFilters {
    severidad?: string;
    modulo?: string;
    resuelto?: boolean;
    fecha_desde?: Date;
    fecha_hasta?: Date;
    codigo?: string;
}

export class ErrorAplicacionService {
    async create(data: CreateErrorAplicacionInput): Promise<Result<any>> {
        try {
            const error = await prisma.errorAplicacion.create({
                data: {
                    codigo: data.codigo || null,
                    severidad: data.severidad as any,
                    mensaje: data.mensaje,
                    stack_trace: data.stack_trace || null,
                    modulo: data.modulo || null,
                    endpoint: data.endpoint || null,
                    metodo_http: data.metodo_http || null,
                    usuario_id: data.usuario_id || null,
                    ip_direccion: data.ip_direccion || null,
                    user_agent: data.user_agent || null,
                    request_body: data.request_body ? (data.request_body as Prisma.InputJsonValue) : null,
                    response_body: data.response_body ? (data.response_body as Prisma.InputJsonValue) : null,
                    contexto: data.contexto ? (data.contexto as Prisma.InputJsonValue) : null
                }
            });

            return ok(serializeBigInts(error));
        } catch (error) {
            console.error('[ErrorAplicacionService.create] Error:', error);
            return err(new BusinessError('Error al crear registro de error', 'CREATE_ERROR', 500));
        }
    }

    async getAll(filters?: ErrorAplicacionFilters, limit: number = 100): Promise<Result<any[]>> {
        try {
            const where: any = {};

            if (filters?.severidad) {
                where.severidad = filters.severidad;
            }
            if (filters?.modulo) {
                where.modulo = filters.modulo;
            }
            if (filters?.resuelto !== undefined) {
                where.resuelto = filters.resuelto;
            }
            if (filters?.fecha_desde || filters?.fecha_hasta) {
                where.creado_en = {};
                if (filters.fecha_desde) {
                    where.creado_en.gte = filters.fecha_desde;
                }
                if (filters.fecha_hasta) {
                    where.creado_en.lte = filters.fecha_hasta;
                }
            }
            if (filters?.codigo) {
                where.codigo = filters.codigo;
            }

            const errors = await prisma.errorAplicacion.findMany({
                where,
                orderBy: {
                    creado_en: 'desc'
                },
                take: limit
            });

            return ok(serializeBigInts(errors));
        } catch (error) {
            console.error('[ErrorAplicacionService.getAll] Error:', error);
            return err(new BusinessError('Error al obtener errores de aplicacion', 'QUERY_ERROR', 500));
        }
    }

    async getById(id: string): Promise<Result<any>> {
        try {
            let bigIntId: bigint;
            try {
                bigIntId = BigInt(id);
            } catch {
                return err(new BusinessError('ID de error invalido', 'INVALID_ID', 400));
            }

            const error = await prisma.errorAplicacion.findFirst({
                where: { id: bigIntId }
            });

            if (!error) {
                return err(new NotFoundError('Error de aplicacion'));
            }

            return ok(serializeBigInts(error));
        } catch (error) {
            console.error('[ErrorAplicacionService.getById] Error:', error);
            return err(new BusinessError('Error al obtener error de aplicacion', 'QUERY_ERROR', 500));
        }
    }

    async acknowledge(id: string, usuario_id: string): Promise<Result<any>> {
        try {
            let bigIntId: bigint;
            try {
                bigIntId = BigInt(id);
            } catch {
                return err(new BusinessError('ID de error invalido', 'INVALID_ID', 400));
            }

            const existing = await prisma.errorAplicacion.findFirst({
                where: { id: bigIntId }
            });

            if (!existing) {
                return err(new NotFoundError('Error de aplicacion'));
            }

            // Acknowledge means marking as seen but not resolved
            // We'll add context note
            const contextoActual = existing.contexto as any || {};
            contextoActual.acknowledged_by = usuario_id;
            contextoActual.acknowledged_at = new Date().toISOString();

            const updated = await prisma.errorAplicacion.update({
                where: { id: bigIntId },
                data: {
                    contexto: contextoActual as Prisma.InputJsonValue
                }
            });

            return ok(serializeBigInts(updated));
        } catch (error) {
            console.error('[ErrorAplicacionService.acknowledge] Error:', error);
            return err(new BusinessError('Error al reconocer error', 'ACKNOWLEDGE_ERROR', 500));
        }
    }

    async resolve(id: string, usuario_id: string, notas?: string): Promise<Result<any>> {
        try {
            let bigIntId: bigint;
            try {
                bigIntId = BigInt(id);
            } catch {
                return err(new BusinessError('ID de error invalido', 'INVALID_ID', 400));
            }

            const existing = await prisma.errorAplicacion.findFirst({
                where: { id: bigIntId }
            });

            if (!existing) {
                return err(new NotFoundError('Error de aplicacion'));
            }

            if (existing.resuelto) {
                return err(new BusinessError('El error ya esta resuelto', 'ALREADY_RESOLVED', 400));
            }

            const contextoActual = existing.contexto as any || {};
            if (notas) {
                contextoActual.resolve_notas = notas;
            }

            const updated = await prisma.errorAplicacion.update({
                where: { id: bigIntId },
                data: {
                    resuelto: true,
                    resuelto_por: usuario_id,
                    resuelto_en: new Date(),
                    contexto: contextoActual as Prisma.InputJsonValue
                }
            });

            return ok(serializeBigInts(updated));
        } catch (error) {
            console.error('[ErrorAplicacionService.resolve] Error:', error);
            return err(new BusinessError('Error al resolver error', 'RESOLVE_ERROR', 500));
        }
    }

    async getStats(): Promise<Result<any>> {
        try {
            // Total errors
            const total = await prisma.errorAplicacion.count();

            // Resolved vs unresolved
            const resueltos = await prisma.errorAplicacion.count({
                where: { resuelto: true }
            });

            const noResueltos = total - resueltos;

            // Count by severity
            const porSeveridad = await prisma.errorAplicacion.groupBy({
                by: ['severidad'],
                _count: true,
                orderBy: {
                    severidad: 'asc'
                }
            });

            // Count by module
            const porModulo = await prisma.errorAplicacion.groupBy({
                by: ['modulo'],
                _count: true,
                where: {
                    modulo: {
                        not: null
                    }
                },
                orderBy: {
                    _count: {
                        modulo: 'desc'
                    }
                }
            });

            // Recent errors (last 24h)
            const hace24h = new Date(Date.now() - 24 * 60 * 60 * 1000);
            const recientes24h = await prisma.errorAplicacion.count({
                where: {
                    creado_en: {
                        gte: hace24h
                    }
                }
            });

            // Critical errors (unresolved)
            const criticosSinResolver = await prisma.errorAplicacion.count({
                where: {
                    severidad: 'CRITICAL',
                    resuelto: false
                }
            });

            return ok({
                total,
                resueltos,
                noResueltos,
                porcentajeResolucion: total > 0 ? Math.round((resueltos / total) * 100) : 0,
                porSeveridad: porSeveridad.map(p => ({
                    severidad: p.severidad,
                    cantidad: p._count
                })),
                porModulo: porModulo.map(p => ({
                    modulo: p.modulo,
                    cantidad: p._count
                })),
                recientes24h,
                criticosSinResolver
            });
        } catch (error) {
            console.error('[ErrorAplicacionService.getStats] Error:', error);
            return err(new BusinessError('Error al obtener estadisticas de errores', 'STATS_ERROR', 500));
        }
    }
}

export const errorAplicacionService = new ErrorAplicacionService();
