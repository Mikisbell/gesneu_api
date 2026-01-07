import { NextRequest, NextResponse } from 'next/server';
import { QueueService } from '@/lib/services/queue.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export const dynamic = 'force-dynamic'; // Asegurar que no se cachee en Vercel

// Shared Secret para proteger el endpoint cron (configurado en Vercel)
const CRON_SECRET = process.env.CRON_SECRET || 'dev_secret_123';

export async function GET(request: NextRequest) {
    try {
        // 1. Verificar autorización (Bearer Token o Header de Vercel Cron)
        const authHeader = request.headers.get('authorization');
        const vercelSignature = request.headers.get('x-vercel-cron-user-agent');

        const isAuthorized =
            (authHeader === `Bearer ${CRON_SECRET}`) ||
            (process.env.NODE_ENV === 'development') || // Permitir dev sin auth estricta por facilidad
            (vercelSignature?.includes('vercel-cron'));

        if (!isAuthorized) {
            return new NextResponse('Unauthorized', { status: 401 });
        }

        // 2. Procesar trabajos
        const queueService = new QueueService();
        // Procesamos un lote de 20 por ejecución (Vercel max duration limit consideration)
        const result = await queueService.processPendingJobs(20);

        return NextResponse.json({
            success: true,
            message: 'Queue processed',
            stats: result
        });

    } catch (error: any) {
        console.error('[Cron Webhooks] Error:', error);
        return NextResponse.json({ success: false, error: error.message }, { status: 500 });
    }
}
