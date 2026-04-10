import { apiHandler } from '@/lib/utils/api-handler';
import { webhookService } from '@/lib/container';
import { CreateWebhookSchema } from '@/lib/validators/webhook.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export const PUT = apiHandler(
    async (req, session, context, body) => {
        const { id } = await context.params; // Next.js params
        try {
            const result = await webhookService.update(id, body, session.user.empresa_id!);
            return ApiResponseHelper.success(result);
        } catch (e: any) {
            if (e.message.includes('no encontrado')) return ApiResponseHelper.error(e.message, 404);
            throw e;
        }
    },
    {
        roles: ['ADMIN'],
        schema: CreateWebhookSchema.partial()
    }
);

export const DELETE = apiHandler(
    async (req, session, context) => {
        const { id } = await context.params;
        try {
            await webhookService.delete(id, session.user.empresa_id!);
            return ApiResponseHelper.success({ deleted: true });
        } catch (e: any) {
            if (e.message.includes('no encontrado')) return ApiResponseHelper.error(e.message, 404);
            throw e;
        }
    },
    { roles: ['ADMIN'] }
);
