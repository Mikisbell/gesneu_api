import { prisma } from '@/lib/prisma';
import { WebhookJob, JobStatus } from '@prisma/client';

export class QueueService {

    /**
     * Encola un trabajo para ser procesado por el worker.
     * @param webhookId ID de la configuración de webhook
     * @param evento Nombre del evento
     * @param payload Datos JSON
     */
    async enqueue(webhookId: string, evento: string, payload: any): Promise<WebhookJob> {
        return await prisma.webhookJob.create({
            data: {
                webhook_id: webhookId,
                evento,
                payload: payload,
                status: JobStatus.PENDING,
                attempts: 0,
                run_at: new Date() // Ejecutar lo antes posible
            }
        });
    }

    /**
     * Procesa los trabajos pendientes.
     * @param batchSize Cantidad máxima de trabajos a procesar en esta ejecución
     */
    async processPendingJobs(batchSize: number = 10): Promise<{ processed: number, successes: number, failures: number }> {
        const now = new Date();

        // 1. Buscar trabajos pendientes que ya deban ejecutarse
        // Usamos una transacción simple para "reservarlos" (aunque sin skip locked por simplicidad en prima, 
        // pero updateMany + find es una estrategia aceptable para bajo volumen)
        // Mejor estrategia con Prisma estándar: Find IDs -> Update Status to PROCESSING -> Process -> Update COMPLETED/FAILED

        const jobs = await prisma.webhookJob.findMany({
            where: {
                status: { in: [JobStatus.PENDING, JobStatus.FAILED] },
                run_at: { lte: now },
                attempts: { lt: 5 } // Hardcoded max retries filter
            },
            take: batchSize,
            orderBy: { run_at: 'asc' }
        });

        if (jobs.length === 0) {
            return { processed: 0, successes: 0, failures: 0 };
        }

        // Marcar como PROCESSING para que otros workers no los tomen (si escalamos)
        // Nota: Esto no es atómico perfecto sin SELECT ... FOR UPDATE, pero sirve para cron de 1 minuto.
        await prisma.webhookJob.updateMany({
            where: { id: { in: jobs.map(j => j.id) } },
            data: { status: JobStatus.PROCESSING }
        });

        let successes = 0;
        let failures = 0;

        // Import dinámico para evitar ciclo, ya que WebhookService usará QueueService para encolar,
        // pero QueueService necesita métodos de envío "reales" que estaban en WebhookService.
        // Refactor ideal: Mover lógica de envío (fetch) a una utilidad pura o mantenerla en WebhookService
        // y que QueueService llame a "executeJob" de WebhookService.
        const { WebhookService } = require('./webhook.service');
        const webhookService = new WebhookService();

        for (const job of jobs) {
            try {
                // Obtener config fresca (url, secret puede cambiar)
                const config = await prisma.webhookConfig.findUnique({ where: { id: job.webhook_id } });

                if (!config || !config.activo) {
                    // Si se borró o desactivó, fallar definitivamente
                    await prisma.webhookJob.update({
                        where: { id: job.id },
                        data: { status: JobStatus.FAILED }
                    });
                    failures++;
                    continue;
                }

                // Ejecutar envío real (usando el método privado hecho público o similar)
                // Vamos a exponer un método en WebhookService que NO encolo, sino que ENVÍE.
                const result = await webhookService.executeJob(config, job.evento, job.payload);

                if (result.success) {
                    await prisma.webhookJob.update({
                        where: { id: job.id },
                        data: { status: JobStatus.COMPLETED, updated_at: new Date() }
                    });
                    successes++;
                } else {
                    throw new Error(result.error || `HTTP ${result.statusCode}`);
                }

            } catch (error: any) {
                failures++;
                const attempts = job.attempts + 1;
                const maxRetries = job.max_retries;
                const nextRun = this.calculateBackoff(attempts);

                const newStatus = attempts >= maxRetries ? JobStatus.FAILED : JobStatus.PENDING; // Volver a PENDING con nueva fecha
                // Si falla definitivamente, se queda en FAILED. Si no, en PENDING para reintento.

                await prisma.webhookJob.update({
                    where: { id: job.id },
                    data: {
                        status: newStatus,
                        attempts: attempts,
                        run_at: nextRun,
                        updated_at: new Date()
                    }
                });
            }
        }

        return { processed: jobs.length, successes, failures };
    }

    /**
     * Backoff Exponencial
     * Intento 1: +1 min
     * Intento 2: +5 min
     * Intento 3: +15 min
     * Intento 4: +60 min
     * Intento 5: +3 horas
     */
    private calculateBackoff(attempt: number): Date {
        const now = new Date();
        let minutesToAdd = 1;

        if (attempt === 1) minutesToAdd = 1;
        else if (attempt === 2) minutesToAdd = 5;
        else if (attempt === 3) minutesToAdd = 15;
        else if (attempt === 4) minutesToAdd = 60;
        else if (attempt >= 5) minutesToAdd = 180;

        return new Date(now.getTime() + minutesToAdd * 60000);
    }
}
