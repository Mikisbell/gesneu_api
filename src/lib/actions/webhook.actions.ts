'use server';

import { prisma } from '@/lib/prisma';
import { requireAuth } from '@/lib/auth/authorization';
import { WebhookEventType } from '@prisma/client';
import { revalidatePath } from 'next/cache';

export async function getWebhooks() {
    const session = await requireAuth();
    // TODO: Filtrar por empresa_id si fuera multi-tenant real
    return await prisma.webhookConfig.findMany({
        orderBy: { creado_en: 'desc' }
    });
}

export async function createWebhook(data: {
    nombre: string;
    url: string;
    secret?: string;
    eventos: WebhookEventType[];
}) {
    const session = await requireAuth();

    // Generar secret si no viene
    const secret = data.secret || crypto.randomUUID().replace(/-/g, '');

    await prisma.webhookConfig.create({
        data: {
            nombre: data.nombre,
            url: data.url,
            secret,
            eventos: data.eventos,
            creado_por: session.user.id
        }
    });

    revalidatePath('/dashboard/ajustes/integraciones');
}

export async function deleteWebhook(id: string) {
    await requireAuth();
    await prisma.webhookConfig.delete({ where: { id } });
    revalidatePath('/dashboard/ajustes/integraciones');
}

export async function toggleWebhook(id: string, activo: boolean) {
    await requireAuth();
    await prisma.webhookConfig.update({
        where: { id },
        data: { activo }
    });
    revalidatePath('/dashboard/ajustes/integraciones');
}
