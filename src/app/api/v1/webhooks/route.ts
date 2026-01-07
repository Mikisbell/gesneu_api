import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth } from '@/lib/auth/authorization';
import { CreateWebhookSchema } from '@/lib/validators/webhook.validator';

// GET: Listar webhooks
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        // Solo ADMIN puede ver/configurar webhooks
        const isAdmin = session.user.roles?.includes('ADMINISTRADOR') || session.user.roles?.includes('ADMIN');
        if (!isAdmin) {
            return ApiResponseHelper.error('Requiere rol de Administrador', 403);
        }

        const webhooks = await prisma.webhookConfig.findMany({
            orderBy: { creado_en: 'desc' }
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

// POST: Crear webhook
export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();
        const isAdmin = session.user.roles?.includes('ADMINISTRADOR') || session.user.roles?.includes('ADMIN');
        if (!isAdmin) {
            return ApiResponseHelper.error('Requiere rol de Administrador', 403);
        }

        const json = await request.json();
        const body = CreateWebhookSchema.parse(json);

        const webhook = await prisma.webhookConfig.create({
            data: {
                ...body,
                creado_por: session.user.id
            }
        });

        return ApiResponseHelper.created(webhook);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
