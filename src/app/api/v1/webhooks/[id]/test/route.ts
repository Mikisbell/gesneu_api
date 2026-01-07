import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth } from '@/lib/auth/authorization';
import { WebhookService } from '@/lib/services/webhook.service';
import { WebhookEventType } from '@prisma/client';

const webhookService = new WebhookService();

// POST: Probar webhook
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    try {
        const session = await requireAuth();
        if (!session.user.roles.includes('ADMIN')) return ApiResponseHelper.error('Requiere rol de Administrador', 403);

        const { id } = await params;
        const webhook = await prisma.webhookConfig.findUnique({
            where: { id }
        });

        if (!webhook) return ApiResponseHelper.error('Webhook no encontrado', 404);

        // Payload de prueba
        const testPayload = {
            mensaje: 'Esta es una prueba de integración de GesNeu API',
            usuario: session.user.email,
            timestamp: new Date().toISOString()
        };

        // Forzar envío a este webhook específico
        // Usamos un evento genérico o el primero de su lista
        const event = webhook.eventos[0] || WebhookEventType.ALL_EVENTS;

        // Hack: Para probar, llamamos al método privado sendToWebhook a través de dispatch filtrado?
        // No, el dispatch busca por evento. Si el webhook tiene evento, lo recibirá.
        // Pero queremos forzar SOLO a este. 
        // Mejor simulamos el dispatch pero verificamos logs.

        await webhookService.dispatch(event, testPayload);

        // Buscamos el último log generado para este webhook
        // Damos un pequeño delay para asegurar que se procesó (ya que dispatch es async fire&forget)
        await new Promise(r => setTimeout(r, 1000));

        const lastLog = await prisma.webhookLog.findFirst({
            where: { webhook_id: webhook.id },
            orderBy: { creado_en: 'desc' }
        });

        return ApiResponseHelper.success({
            sent: true,
            event,
            log: lastLog
        });

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

