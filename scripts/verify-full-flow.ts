
import { prisma } from '../src/lib/prisma';
import { WebhookService } from '../src/lib/services/webhook.service';
import { InspeccionService } from '../src/lib/services/inspeccion.service';
import { WebhookEventType, TipoAlertaEnum } from '@prisma/client';

async function main() {
    console.log('🚀 Iniciando Prueba Extrema E2E...');

    // 1. SETUP: Limpieza y Datos Previos
    const adminUser = await prisma.usuario.findFirst();
    if (!adminUser) throw new Error('No admin user found. Seed the DB first.');

    const empresa = await prisma.empresa.findFirst();
    if (!empresa) throw new Error('No empresa found.');

    console.log('✅ Setup: Usuario y Empresa encontrados.');

    // 2. FRONTEND SIMULATION: Crear Webhook via DB (Simulando Server Action)
    const webhookUrl = 'https://webhook.site/uuid-simulado-test';
    const webhook = await prisma.webhookConfig.create({
        data: {
            nombre: 'E2E Test Webhook',
            url: webhookUrl,
            secret: 'secret_test_123',
            eventos: [WebhookEventType.ALERTA_CRITICAL],
            activo: true,
            creado_por: adminUser.id
        }
    });
    console.log(`✅ UI Action: Webhook creado con ID ${webhook.id}`);

    // 3. BACKEND LOGIC: Trigger Evento (Inspección Baja Presión)
    // Crear modelo y neumático temporal
    const modelo = await prisma.modeloNeumatico.create({
        data: {
            nombre_modelo: 'E2E Model',
            medida: '11R22',
            fabricante_id: (await prisma.fabricanteNeumatico.findFirst())?.id!,
            profundidad_original_mm: 20,
            presion_recomendada_psi: 100 // Should alert at < 80 (80 PSI)
        }
    });

    const neumatico = await prisma.neumatico.create({
        data: {
            modelo_id: modelo.id,
            empresa_id: empresa.id,
            numero_serie: 'E2E-TIRE-001',
            fecha_compra: new Date(),
            estad_actual: 'EN_STOCK',
            profundidad_remanente_actual_mm: 20,
            ubicacion_almacen_id: (await prisma.almacen.findFirst())?.id
        }
    });

    console.log('✅ Data: Neumático de prueba creado.');

    const inspeccionService = new InspeccionService();
    // Registrar 60 PSI (Muy bajo vs 100 recomendado)
    await inspeccionService.registrarManual({
        neumatico_id: neumatico.id,
        presion_psi: 60,
        temperatura_c: 25,
        observaciones: 'E2E Test Pressure'
    }, adminUser.id);

    console.log('✅ Logic: Inspección registrada (60 PSI).');

    // 4. VERIFICATION: Validar impacto en DB (Lo que vería el Frontend)

    // Check Alerta
    const alerta = await prisma.alerta.findFirst({
        where: { neumatico_id: neumatico.id, tipo: TipoAlertaEnum.PRESION_BAJA }
    });

    if (!alerta) throw new Error('❌ FALLO: No se generó la Alerta en DB.');
    console.log(`✅ DB Verify: Alerta generada correctamente (Severidad: ${alerta.severidad}).`);

    // Check Webhook Queue (El "Efecto Secundario")
    const job = await prisma.webhookJob.findFirst({
        where: { webhook_id: webhook.id }
    });

    if (!job) throw new Error('❌ FALLO: No se encoló el trabajo del Webhook.');
    console.log(`✅ DB Verify: Job de Webhook encolado (Status: ${job.status}).`);

    // 5. CLEANUP
    await prisma.webhookJob.deleteMany({ where: { webhook_id: webhook.id } });
    await prisma.webhookConfig.delete({ where: { id: webhook.id } });
    await prisma.alerta.deleteMany({ where: { neumatico_id: neumatico.id } });
    await prisma.lecturaPresion.deleteMany({ where: { neumatico_id: neumatico.id } });
    await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: neumatico.id } });
    await prisma.neumatico.delete({ where: { id: neumatico.id } });
    await prisma.modeloNeumatico.delete({ where: { id: modelo.id } });

    console.log('✅ Cleanup: Datos de prueba eliminados.');
    console.log('🎉 PRUEBA EXTREMA DE FLUJO COMPLETO: ÉXITO ROTUNDO');
}

main()
    .catch(e => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
