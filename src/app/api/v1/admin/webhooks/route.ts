
import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, isAdmin } from '@/lib/auth/authorization';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { AdminWebhookSearchSchema } from '@/lib/validators/admin.validator';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();

        if (!isAdmin(session)) {
            return ApiResponseHelper.forbidden('Solo administradores pueden ver webhooks');
        }

        // Validate query params with Zod
        const { searchParams } = new URL(request.url);
        const params = Object.fromEntries(searchParams.entries());
        const validatedParams = AdminWebhookSearchSchema.parse(params);

        const { empresa_id, exitoso, limit } = validatedParams;

        // Build where clause for logs
        const logsWhere: any = {};
        if (empresa_id) logsWhere.webhook = { empresa_id };
        if (exitoso !== undefined) {
            logsWhere.exitoso = exitoso;
        }

        const [webhooks, logs, stats] = await Promise.all([
            // All webhooks
            prisma.webhookConfig.findMany({
                orderBy: { creado_en: 'desc' },
                include: {
                    empresa: { select: { nombre: true } },
                    _count: { select: { logs: true } }
                }
            }),

            // Recent logs
            prisma.webhookLog.findMany({
                where: logsWhere,
                take: limit,
                orderBy: { creado_en: 'desc' },
                include: {
                    webhook: {
                        select: {
                            nombre: true,
                            url: true,
                            empresa: { select: { nombre: true } }
                        }
                    }
                }
            }),

            // Stats (last 24h)
            Promise.all([
                prisma.webhookLog.count({
                    where: {
                        creado_en: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
                    }
                }),
                prisma.webhookLog.count({
                    where: {
                        exitoso: true,
                        creado_en: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
                    }
                }),
                prisma.webhookLog.count({
                    where: {
                        exitoso: false,
                        creado_en: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
                    }
                })
            ])
        ]);

        const [total24h, success24h, failed24h] = stats;
        const successRate = total24h > 0 ? Math.round((success24h / total24h) * 100) : 100;

        return ApiResponseHelper.success({
            webhooks,
            logs,
            stats: {
                total24h,
                success24h,
                failed24h,
                successRate
            }
        });
    } catch (error) {
        console.error('[Webhook Console] Error:', error);
        return ApiResponseHelper.handleError(error);
    }
}
