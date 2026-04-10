import { QueueService } from '@/lib/services/queue.service';
import { prisma } from '@/lib/prisma';
import { WebhookEventType } from '@prisma/client';
import { getOrCreateTestEnterprise } from '@/__tests__/helpers/database-helpers';

// Mock WebhookService to avoid actual HTTP calls and circular dependency issues in test environment if any
// But for integration test we want to use the real QueueService flow.
// We will mock only the fetch call inside WebhookService logic or just let it fail to test retries.

jest.mock('@/lib/services/webhook.service', () => {
    return {
        WebhookService: class MockWebhookService {
            async executeJob(config: any, event: any, payload: any) {
                // Simular éxito para evento 'SUCCESS_TEST'
                if (event === 'SUCCESS_TEST') {
                    return { success: true, statusCode: 200 };
                }
                // Simular fallo para evento 'FAIL_TEST'
                if (event === 'FAIL_TEST') {
                    return { success: false, statusCode: 500, error: 'Simulated 500' };
                }
                return { success: true, statusCode: 200 };
            }
        }
    }
});

describe('QueueService Integration', () => {
    let queueService: QueueService;
    let webhookId: string;

    beforeAll(async () => {
        queueService = new QueueService();
        // Create or get test enterprise first
        const empresa = await getOrCreateTestEnterprise();
        // Crear un webhook dummy
        const wh = await prisma.webhookConfig.create({
            data: {
                nombre: 'Queue Test',
                url: 'http://test.local',
                secret: 'secret',
                eventos: ['ALL_EVENTS'],
                activo: true,
                empresa_id: empresa.id
            }
        });
        webhookId = wh.id;
    });

    afterAll(async () => {
        await prisma.webhookJob.deleteMany({ where: { webhook_id: webhookId } });
        await prisma.webhookConfig.delete({ where: { id: webhookId } });
    });

    beforeEach(async () => {
        await prisma.webhookJob.deleteMany({ where: { webhook_id: webhookId } });
    });

    it('should enqueue a job with status PENDING', async () => {
        const job = await queueService.enqueue(webhookId, 'TEST_EVENT', { foo: 'bar' });
        expect(job.status).toBe('PENDING');
        expect(job.payload).toEqual({ foo: 'bar' });
        expect(job.attempts).toBe(0);
    });

    it('should process a job successfully', async () => {
        await queueService.enqueue(webhookId, 'SUCCESS_TEST', {});

        const result = await queueService.processPendingJobs(10);

        expect(result.processed).toBe(1);
        expect(result.successes).toBe(1);
        expect(result.failures).toBe(0);

        const job = await prisma.webhookJob.findFirst({ where: { evento: 'SUCCESS_TEST' } });
        expect(job?.status).toBe('COMPLETED');
    });

    it('should handle failures and schedule retry', async () => {
        const jobCreated = await queueService.enqueue(webhookId, 'FAIL_TEST', {});

        const result = await queueService.processPendingJobs(10);

        expect(result.processed).toBe(1);
        expect(result.successes).toBe(0);
        expect(result.failures).toBe(1);

        const job = await prisma.webhookJob.findUnique({ where: { id: jobCreated.id } });
        expect(job?.status).toBe('PENDING'); // Should be pending for retry
        expect(job?.attempts).toBe(1);

        // Verificar que run_at es futuro (aprox 1 min)
        const diff = job!.run_at.getTime() - new Date().getTime();
        expect(diff).toBeGreaterThan(50000); // Al menos 50s en el futuro
    });
});
