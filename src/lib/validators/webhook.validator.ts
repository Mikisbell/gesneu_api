import { z } from 'zod';
import { WebhookEventType } from '@prisma/client';

export const WebhookEventTypeEnum = z.nativeEnum(WebhookEventType);

export const CreateWebhookSchema = z.object({
    nombre: z.string().min(3, "El nombre debe tener al menos 3 caracteres"),
    url: z.string().url("Debe ser una URL válida").startsWith("https://", "La URL debe ser segura (HTTPS)"),
    secret: z.string().min(10, "El secreto debe tener al menos 10 caracteres"),
    eventos: z.array(WebhookEventTypeEnum).min(1, "Debe seleccionar al menos un evento"),
    activo: z.boolean().optional().default(true)
});

export const UpdateWebhookSchema = CreateWebhookSchema.partial().extend({
    // Permitir ID para buscar, pero no para actualizar
});

export type CreateWebhookDTO = z.infer<typeof CreateWebhookSchema>;
export type UpdateWebhookDTO = z.infer<typeof UpdateWebhookSchema>;
