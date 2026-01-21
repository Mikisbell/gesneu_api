
import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, isAdmin } from '@/lib/auth/authorization';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { AdminAuditSearchSchema } from '@/lib/validators/admin.validator';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();

        if (!isAdmin(session)) {
            return ApiResponseHelper.forbidden('Solo administradores pueden ver el audit trail');
        }

        // Validate query params with Zod
        const { searchParams } = new URL(request.url);
        const params = Object.fromEntries(searchParams.entries());
        const validatedParams = AdminAuditSearchSchema.parse(params);

        const { search, operacion, tabla, usuario_id, empresa_id, fecha_desde, fecha_hasta, limit, offset } = validatedParams;

        // Build where clause
        const where: any = {};

        if (search) {
            where.OR = [
                { nombre_tabla: { contains: search, mode: 'insensitive' } },
                { usuario_app: { contains: search, mode: 'insensitive' } },
                { entidad_id: { contains: search, mode: 'insensitive' } }
            ];
        }

        if (operacion) where.operacion = operacion;
        if (tabla) where.nombre_tabla = tabla;
        if (usuario_id) where.usuario_app_id = usuario_id;

        // Fix: Filter by empresa_id via User relation
        if (empresa_id) {
            where.usuario = { empresa_id: empresa_id };
        }

        if (fecha_desde || fecha_hasta) {
            where.timestamp_log = {};
            if (fecha_desde) where.timestamp_log.gte = new Date(fecha_desde);
            if (fecha_hasta) where.timestamp_log.lte = new Date(fecha_hasta);
        }

        // Fetch logs with count
        const [logs, total] = await Promise.all([
            prisma.auditoriaLog.findMany({
                where,
                take: limit,
                skip: offset,
                orderBy: { timestamp_log: 'desc' },
                include: {
                    usuario: { select: { username: true, email: true, empresa: { select: { nombre: true } } } }
                }
            }),
            prisma.auditoriaLog.count({ where })
        ]);

        // Serialize BigInt IDs
        const serializedLogs = logs.map(log => ({
            id: log.id.toString(),
            timestamp_log: log.timestamp_log,
            operacion: log.operacion,
            nombre_tabla: log.nombre_tabla,
            entidad_id: log.entidad_id,
            usuario_app: log.usuario_app,
            ip_direccion: log.ip_direccion,
            datos_antiguos: log.datos_antiguos,
            datos_nuevos: log.datos_nuevos,
            cambios: log.cambios,
            usuario: log.usuario,
            // Map empresa from user relation since AuditoriaLog doesn't have it directly
            empresa: log.usuario?.empresa
        }));

        // Get distinct tables for filter
        const tables = await prisma.auditoriaLog.groupBy({
            by: ['nombre_tabla'],
            _count: true,
            orderBy: { _count: { nombre_tabla: 'desc' } },
            take: 20
        });

        return ApiResponseHelper.success({
            logs: serializedLogs,
            filters: {
                tables: tables.map(t => t.nombre_tabla)
            },
            pagination: {
                total,
                limit,
                offset,
                hasMore: offset + logs.length < total
            }
        });
    } catch (error) {
        console.error('[Admin Audit] Error:', error);
        return ApiResponseHelper.handleError(error);
    }
}
