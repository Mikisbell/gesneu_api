
import { prisma } from '@/lib/prisma';
import { InspeccionService } from '@/lib/services/inspeccion.service';
import { WebhookEventType, TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';

// Services
const inspeccionService = new InspeccionService();

describe('System E2E: Webhooks & Alerts Flow', () => {
    let empresaId: string;
    let usuarioId: string;
    let webhookId: string;
    let neumaticoId: string;
    let modeloId: string;
    let fabricanteId: string;

    // Setup global para la suite
    beforeAll(async () => {
        // 1. Crear Empresa y Usuario Admin
        const empresa = await prisma.empresa.create({
            data: { nombre: 'E2E Corp', ruc: `20${Date.now()}999`.substring(0, 20) }
        });
        empresaId = empresa.id;

        const usuario = await prisma.usuario.create({
            data: {
                empresa_id: empresa.id,
                username: `admin_e2e_${Date.now()}`,
                email: `admin_e2e_${Date.now()}@test.com`,
                password_hash: 'hash',
                nombre_completo: 'Admin E2E'
            }
        });
        usuarioId = usuario.id;

        // 2. Crear Configuración Webhook (Simulando UI Action)
        const webhook = await prisma.webhookConfig.create({
            data: {
                nombre: 'E2E Validation Webhook',
                url: 'https://webhook.site/e2e-test-endpoint',
                secret: 'e2e_secret_key',
                eventos: [WebhookEventType.ALERTA_CRITICAL], // Suscrito a alertas críticas
                activo: true,
                empresa_id: empresaId,
                creado_por: usuarioId
            }
        });
        webhookId = webhook.id;

        // 3. Crear Catálogo Neumáticos
        const fab = await prisma.fabricanteNeumatico.create({ data: { nombre: 'Fab E2E' } });
        fabricanteId = fab.id;

        const mod = await prisma.modeloNeumatico.create({
            data: {
                fabricante_id: fab.id,
                nombre_modelo: 'Model X',
                medida: '11R22',
                profundidad_original_mm: 15,
                presion_recomendada_psi: 100 // Alert threshold < 80 PSI
            }
        });
        modeloId = mod.id;

        const neum = await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: mod.id,
                numero_serie: 'TIRE-E2E-001',
                fecha_compra: new Date(),
                profundidad_remanente_actual_mm: 15,
                estado_actual: 'EN_STOCK'
            }
        });
        neumaticoId = neum.id;
    });

    afterAll(async () => {
        // Cleanup en orden inverso - with guards for undefined IDs
        if (webhookId) {
            await prisma.webhookJob.deleteMany({ where: { webhook_id: webhookId } }).catch(() => {});
            await prisma.webhookConfig.delete({ where: { id: webhookId } }).catch(() => {});
        }
        if (neumaticoId) {
            await prisma.alerta.deleteMany({ where: { neumatico_id: neumaticoId } }).catch(() => {});
            await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: neumaticoId } }).catch(() => {});
            await prisma.lecturaPresion.deleteMany({ where: { neumatico_id: neumaticoId } }).catch(() => {});
            await prisma.neumatico.delete({ where: { id: neumaticoId } }).catch(() => {});
        }
        if (modeloId) {
            await prisma.modeloNeumatico.delete({ where: { id: modeloId } }).catch(() => {});
        }
        if (fabricanteId) {
            await prisma.fabricanteNeumatico.delete({ where: { id: fabricanteId } }).catch(() => {});
        }
        if (usuarioId) {
            await prisma.usuario.delete({ where: { id: usuarioId } }).catch(() => {});
        }
        if (empresaId) {
            await prisma.empresa.delete({ where: { id: empresaId } }).catch(() => {});
        }

        await prisma.$disconnect();
    });

    it('Debe ejecutar el ciclo completo: Inspección -> Alerta -> Webhook Queue', async () => {
        // A. Acción de Negocio: Inspección con Presión Crítica
        // 50 PSI es < 80% de 100 (Threshold 80). Debe generar Alerta CRITICAL.
        await inspeccionService.registrarManual({
            neumatico_id: neumaticoId,
            presion_psi: 50,
            temperatura_c: 30,
            observaciones: 'E2E Low Pressure Event'
        }, usuarioId);

        // B. Verificación de Alerta (Backend Logic)
        const alerta = await prisma.alerta.findFirst({
            where: {
                neumatico_id: neumaticoId,
                tipo: TipoAlertaEnum.PRESION_BAJA
            }
        });

        expect(alerta).toBeDefined();
        expect(alerta?.severidad).toBe(SeveridadAlertaEnum.CRITICAL);
        console.log('✅ Paso 1: Alerta generada en DB');

        // C. Verificación de Webhook Job (Integration Logic)
        // El trigger debió encolar el trabajo para el webhook suscrito
        // Esperamos un pequeño delay si fuera async puro, pero en test environment suele ser sequential promises
        const job = await prisma.webhookJob.findFirst({
            where: {
                webhook_id: webhookId,
                status: 'PENDING'
            }
        });

        expect(job).toBeDefined();
        expect(job?.evento).toBe('ALERTA_CRITICAL'); // El evento disparado para alertas críticas es este
        console.log('✅ Paso 2: Webhook Job encolado en DB');

        // Validación extra: Payload del trabajo contiene info correcta
        const payload: any = job?.payload;
        console.log('🔍 DEBUG PAYLOAD:', JSON.stringify(payload, null, 2));

        // Ajuste: El payload en DB es la data cruda. El wrapper { data: ... } se añade al enviar.
        expect(payload.tipo).toBe(TipoAlertaEnum.PRESION_BAJA);
        expect(payload.neumatico.numero_serie).toBe('TIRE-E2E-001');
    });
});
