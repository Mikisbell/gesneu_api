import { createHmac } from 'crypto';
import { prisma } from '@/lib/prisma';
import { WebhookEventType, WebhookConfig } from '@prisma/client';

export class WebhookService {

    /**
     * Envía un evento a todos los webhooks configurados y activos
     * que estén suscritos a este tipo de evento (o ALL_EVENTS).
     */
    async dispatch(event: WebhookEventType, payload: any, empresaId: string): Promise<void> {
        // 1. Buscar webhooks suscritos de la empresa correcta
        const webhooks = await prisma.webhookConfig.findMany({
            where: {
                activo: true,
                empresa_id: empresaId,
                OR: [
                    { eventos: { has: event } },
                    { eventos: { has: WebhookEventType.ALL_EVENTS } }
                ]
            }
        });

        if (webhooks.length === 0) return;

        console.log(`[WebhookService] Enqueuing event ${event} for ${webhooks.length} subscribers`);

        // 2. Encolar en lugar de enviar directo
        // Evitamos ciclo de dependencias usando import dinámico o instanciando si es necesario.
        // Pero dado que QueueService es new implementation y no tiene dependencias graves, podemos importar.
        // NOTA: Para evitar circular dependency, idealmente QueueService no debería importar WebhookService en top-level si WebhookService importa QueueService.
        // Aquí QueueService necesita executeJob. Rompemos el ciclo haciendo QueueService -> WebhookService.executeJob y WebhookService -> QueueService.enqueue.
        // Usaremos require para QueueService aquí para estar seguros.

        const { QueueService } = require('./queue.service');
        const queueService = new QueueService();

        const promises = webhooks.map(webhook => queueService.enqueue(webhook.id, event, payload));
        await Promise.all(promises);
    }

    /**
     * Lógica pura de envío HTTP y log. 
     * Usada por el Worker (QueueService).
     */
    async executeJob(webhook: WebhookConfig, event: string, payload: any): Promise<{ success: boolean; statusCode?: number; error?: string }> {
        // Convertir string event de DB a Enum si fuera necesario para headers, pero string es seguro
        const timestamp = Date.now();
        const payloadString = JSON.stringify({
            id: crypto.randomUUID(),
            event,
            created_at: new Date().toISOString(),
            data: payload
        });

        // Firma HMAC-SHA256
        const signature = this.generateSignature(payloadString, webhook.secret);

        let responseBody: string | undefined;
        let statusCode: number | undefined;
        let exitoso = false;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

            const response = await fetch(webhook.url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Webhook-Signature': signature,
                    'X-Webhook-Timestamp': timestamp.toString(),
                    'X-Webhook-Event': event,
                    'User-Agent': 'GesNeu-Webhook-Service/1.0'
                },
                body: payloadString,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            statusCode = response.status;
            const text = await response.text();
            responseBody = text.slice(0, 1000);

            if (response.ok) {
                exitoso = true;
            } else {
                console.warn(`[WebhookService] Failed to send to ${webhook.url}: ${statusCode}`);
            }

        } catch (error: any) {
            console.error(`[WebhookService] Error sending to ${webhook.url}:`, error);
            responseBody = error.message?.slice(0, 1000);
            statusCode = 0; // Error de red/timeout
        }

        // Registrar Log (Auditoría de intento)
        // Opcional: Podríamos dejar que el job guarde el log final, pero es bueno tener log de cada intento http
        await prisma.webhookLog.create({
            data: {
                webhook_id: webhook.id,
                evento: event,
                payload: payload as any,
                status_code: statusCode,
                response: responseBody,
                exitoso,
                intentos: 1 // Este log representa 1 intento HTTP individual
            }
        });

        return {
            success: exitoso,
            statusCode,
            error: exitoso ? undefined : (responseBody || 'Unknown error')
        };
    }

    // --- Legacy Private Method Removed ---
    // private async sendToWebhook(...) { ... }

    // --- CRUD Methods (Migration from API Routes) ---

    async getAll(empresaId: string) {
        // Ocultar secret parcialmente handled in Service or Transformer?
        // Service should return domain entities. Transformer/Serializer handles view.
        // But for simplicity, we return sanitized here or raw?
        // Let's return Raw and let Route standardizer handle it? Or sanitize here.
        // Security best practice: Don't leak secrets from Service if possible.
        const webhooks = await prisma.webhookConfig.findMany({
            where: { empresa_id: empresaId },
            orderBy: { id: 'desc' }
        });

        return webhooks.map(w => ({
            ...w,
            secret: w.secret.substring(0, 4) + '****'
        }));
    }

    async findById(id: string, empresaId: string) {
        return prisma.webhookConfig.findFirst({
            where: { id, empresa_id: empresaId }
        });
    }

    async create(data: any, userId: string, empresaId: string) {
        return prisma.webhookConfig.create({
            data: {
                ...data,
                creado_por: userId,
                empresa_id: empresaId
            }
        });
    }

    async update(id: string, data: any, empresaId: string) {
        const count = await prisma.webhookConfig.updateMany({
            where: { id, empresa_id: empresaId },
            data
        });
        if (count.count === 0) throw new Error('Webhook no encontrado o sin permiso');
        return { id, ...data };
    }

    async delete(id: string, empresaId: string) {
        const result = await prisma.webhookConfig.deleteMany({
            where: { id, empresa_id: empresaId }
        });
        if (result.count === 0) throw new Error('Webhook no encontrado o sin permiso');
        return true;
    }

    /**
     * Genera firma HMAC-SHA256
     */
    private generateSignature(payload: string, secret: string): string {
        return createHmac('sha256', secret)
            .update(payload)
            .digest('hex');
    }
}
