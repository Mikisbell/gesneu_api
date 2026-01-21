
import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, isAdmin } from '@/lib/auth/authorization';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();

        console.log('[Admin Dashboard] Checking access for user:', session.user.email);
        console.log('[Admin Dashboard] User roles:', session.user.roles);

        if (!isAdmin(session)) {
            console.log('[Admin Dashboard] Access Denied. IsAdmin returned false.');
            return ApiResponseHelper.forbidden('Solo administradores pueden ver el dashboard');
        }

        const now = new Date();
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

        const [
            tenantsCount, tenantsTrend,
            usersCount, usersTrend,
            alertsSummary,
            webhooksSuccessRate,
            activeSessions,
            recentActivity
        ] = await Promise.all([
            // Tenants
            prisma.empresa.count(),
            prisma.empresa.count({ where: { creado_en: { gte: monthStart } } }),

            // Users
            prisma.usuario.count(),
            prisma.usuario.count({ where: { creado_en: { gte: monthStart } } }),

            // Alerts Summary (using 'tipo' not 'tipo_alerta')
            prisma.alerta.groupBy({
                by: ['severidad'],
                _count: { severidad: true },
                where: { leida: false }
            }),

            // Webhooks Success Rate (using webhookConfig and webhookLog)
            prisma.webhookLog.groupBy({
                by: ['exitoso'],
                _count: { exitoso: true },
                where: { creado_en: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } }
            }),

            // Active Sessions (approximate by recent activity in audit log last 24h distinct users)
            prisma.auditoriaLog.findMany({
                where: { timestamp_log: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } },
                distinct: ['usuario_app_id'],
                select: { usuario_app_id: true }
            }).then(logs => logs.length),

            // Recent global activity
            prisma.auditoriaLog.findMany({
                take: 5,
                orderBy: { timestamp_log: 'desc' },
                include: {
                    usuario: { select: { username: true } },
                    // empresa: { select: { nombre: true } } // Removed as AuditoriaLog doesn't have direct relation
                }
            })
        ]);

        const totalWebhooks = webhooksSuccessRate.reduce((acc, curr) => acc + curr._count.exitoso, 0);
        const successWebhooks = webhooksSuccessRate.find(w => w.exitoso)?._count.exitoso || 0;
        const successRate = totalWebhooks > 0 ? (successWebhooks / totalWebhooks) * 100 : 100;

        // Serialize BigInt IDs
        const serializedActivity = recentActivity.map(log => ({
            id: log.id.toString(),
            operacion: log.operacion,
            nombre_tabla: log.nombre_tabla,
            timestamp_log: log.timestamp_log,
            usuario: log.usuario ? log.usuario.username : 'Sistema'
        }));

        // Match frontend DashboardData interface exactly
        const criticalAlerts = alertsSummary.find(a => a.severidad === 'CRITICAL')?._count.severidad || 0;
        const warningAlerts = alertsSummary.find(a => a.severidad === 'WARNING')?._count.severidad || 0;
        const infoAlerts = alertsSummary.find(a => a.severidad === 'INFO')?._count.severidad || 0;

        // Determine status based on alerts
        let healthStatus: 'OPTIMAL' | 'WARNING' | 'CRITICAL' = 'OPTIMAL';
        if (criticalAlerts > 0) healthStatus = 'CRITICAL';
        else if (warningAlerts > 0) healthStatus = 'WARNING';

        return ApiResponseHelper.success({
            // stats object matching DashboardStats interface
            stats: {
                tenants: { value: tenantsCount, trend: tenantsTrend, label: 'Empresas' },
                users: { value: usersCount, todayNew: 0, weekNew: usersTrend, label: 'Usuarios' },
                neumaticos: { value: 0, label: 'Neumáticos' }, // Placeholder
                vehiculos: { value: 0, label: 'Vehículos' }, // Placeholder
                operations: { value: serializedActivity.length, label: 'Operaciones' }
            },
            // alerts object matching AlertsSummary interface
            alerts: {
                critical: criticalAlerts,
                warning: warningAlerts,
                unresolved: criticalAlerts + warningAlerts + infoAlerts
            },
            // systemHealth object matching HealthStatus interface
            systemHealth: {
                status: healthStatus,
                webhookSuccessRate: Math.round(successRate),
                webhooksTotal24h: totalWebhooks,
                webhooksFailed24h: totalWebhooks - successWebhooks,
                activeSessions
            },
            // recentActivity array matching ActivityLog interface
            recentActivity: serializedActivity
        });
    } catch (error) {
        console.error('[Admin Dashboard] Error:', error);
        return ApiResponseHelper.handleError(error);
    }
}
