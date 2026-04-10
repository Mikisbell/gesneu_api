import { apiHandler } from '@/lib/utils/api-handler';
import { webhookService } from '@/lib/container';
import { CreateWebhookSchema } from '@/lib/validators/webhook.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export const GET = apiHandler(
    async (req, session) => {
        return webhookService.getAll(session.user.empresa_id!);
    },
    { roles: ['ADMIN'] }
);

export const POST = apiHandler(
    async (req, session, _, body) => {
        // Note: apiHandler parser might return typed body if generic is used, 
        // implies we trust it or cast it. using schema option.
        const webhook = await webhookService.create(
            body,
            session.user.id,
            session.user.empresa_id!
        );
        return ApiResponseHelper.created(webhook);
    },
    {
        roles: ['ADMIN'],
        schema: CreateWebhookSchema
    }
);
