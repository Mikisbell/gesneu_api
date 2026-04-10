
import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, isAdmin } from '@/lib/auth/authorization';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { MULTI_TENANT_ENABLED, featureDisabledResponse } from '@/lib/features';

export const runtime = 'nodejs';

interface RouteParams {
    params: Promise<{ id: string }>;
}

export async function GET(request: NextRequest, { params }: RouteParams) {
    if (!MULTI_TENANT_ENABLED) {
        return featureDisabledResponse(
            'Gestión multi-tenant',
            'El sistema opera en modo single-tenant. Gestión de empresas no disponible hasta activar multi-tenant.'
        );
    }

    try {
        const session = await requireAuth();

        if (!isAdmin(session)) {
            return ApiResponseHelper.forbidden('Solo administradores pueden ver detalles de empresa');
        }

        const { id } = await params;

        // Fetch tenant with all related data
        const [tenant, users, recentAlerts, recentActivity] = await Promise.all([
            // Main tenant data with counts
            prisma.empresa.findUnique({
                where: { id },
                include: {
                    _count: {
                        select: {
                            usuarios: true,
                            vehiculos: true,
                            neumaticos: true
                            // alertas: true // Removed as Alerta doesn't have direct relation to Empresa
                        }
                    }
                }
            }),

            // Users of this tenant
            prisma.usuario.findMany({
                where: { empresa_id: id },
                select: {
                    id: true,
                    username: true,
                    email: true,
                    nombre_completo: true,
                    rol: true,
                    activo: true,
                    creado_en: true
                },
                orderBy: { creado_en: 'desc' },
                take: 10
            }),

            // Recent alerts for this tenant (via relations)
            prisma.alerta.findMany({
                where: {
                    OR: [
                        { neumatico: { empresa_id: id } },
                        { vehiculo: { empresa_id: id } }
                    ]
                },
                orderBy: { creada_en: 'desc' },
                take: 5,
                select: {
                    id: true,
                    tipo: true,
                    severidad: true,
                    mensaje: true,
                    leida: true,
                    creada_en: true
                }
            }),

            // Recent audit activity (via user relation)
            prisma.auditoriaLog.findMany({
                where: { usuario: { empresa_id: id } },
                orderBy: { timestamp_log: 'desc' },
                take: 5,
                include: {
                    usuario: { select: { username: true } }
                }
            })
        ]);

        if (!tenant) {
            return ApiResponseHelper.notFound('Empresa no encontrada');
        }

        // Serialize BigInt IDs from audit logs
        const serializedActivity = recentActivity.map(log => ({
            id: log.id.toString(),
            operacion: log.operacion,
            nombre_tabla: log.nombre_tabla,
            timestamp_log: log.timestamp_log,
            usuario: log.usuario
        }));

        // Map API response to expected format
        const tenantData = {
            ...tenant,
            _count: {
                ...tenant._count,
                alertas: 0 // Placeholder as we can't count efficiently without direct relation
            }
        };

        return ApiResponseHelper.success({
            tenant: tenantData,
            users,
            recentAlerts: recentAlerts.map(a => ({
                ...a,
                tipo_alerta: a.tipo // Map internal 'tipo' to API 'tipo_alerta'
            })),
            recentActivity: serializedActivity
        });
    } catch (error) {
        console.error('[Tenant Detail] Error:', error);
        return ApiResponseHelper.handleError(error);
    }
}
