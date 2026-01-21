
import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requireRole } from '@/lib/auth/authorization';
import { CreateWebhookSchema } from '@/lib/validators/webhook.validator';

// GET: Listar webhooks (Scoped by Tenant)
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requireRole(session, ['ADMIN', 'ADMINISTRADOR']);

        const webhooks = await prisma.webhookConfig.findMany({
            where: {
                empresa_id: session.user.empresa_id
            },
            orderBy: { id: 'desc' }
        });

        // Ocultar secret parcialmente
        const safeWebhooks = webhooks.map(w => ({
            ...w,
            secret: w.secret.substring(0, 4) + '****'
        }));

        return ApiResponseHelper.success(safeWebhooks);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

// POST: Crear webhook (Scoped by Tenant)
export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();
        requireRole(session, ['ADMIN', 'ADMINISTRADOR']);

        const json = await request.json();
        const body = CreateWebhookSchema.parse(json);

        const webhook = await prisma.webhookConfig.create({
            data: {
                ...body,
                creado_por: session.user.id,
                empresa_id: session.user.empresa_id || '00000000-0000-0000-0000-000000000000' // Fallback handled by DB default usually
            }
        });

        return ApiResponseHelper.created(webhook);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
