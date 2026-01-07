import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth } from '@/lib/auth/authorization';
import { CreateWebhookSchema } from '@/lib/validators/webhook.validator';

// PUT: Actualizar webhook
export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    try {
        const session = await requireAuth();
        if (!session.user.roles.includes('ADMIN')) return ApiResponseHelper.error('Requiere rol de Administrador', 403);

        const { id } = await params;
        const json = await request.json();
        const body = CreateWebhookSchema.partial().parse(json);

        const updated = await prisma.webhookConfig.update({
            where: { id },
            data: body
        });

        return ApiResponseHelper.success(updated);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

// DELETE: Eliminar webhook
export async function DELETE(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
    try {
        const session = await requireAuth();
        if (!session.user.roles.includes('ADMIN')) return ApiResponseHelper.error('Requiere rol de Administrador', 403);

        const { id } = await params;
        await prisma.webhookConfig.delete({
            where: { id }
        });

        return ApiResponseHelper.success({ deleted: true });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

