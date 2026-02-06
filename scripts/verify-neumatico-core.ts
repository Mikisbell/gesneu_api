
import 'dotenv/config';
import { neumaticoService } from '../src/lib/services/neumatico.service';
import { fabricanteService } from '../src/lib/services/fabricante.service';
import { modeloNeumaticoService } from '../src/lib/services/modelo-neumatico.service';
import { prisma } from '../src/lib/prisma';
import { DEFAULT_TENANT_ID, DEFAULT_TENANT_NAME, DEFAULT_TENANT_RUC } from '../src/lib/constants';

async function main() {
    console.log('🛞 Verifying Neumatico Core Service...');

    // 0. Setup Dependencies (Tenant, User, Manufacturer, Model)
    console.log('   Setting up context...');

    // Ensure Tenant
    await prisma.empresa.upsert({
        where: { id: DEFAULT_TENANT_ID },
        update: {},
        create: {
            id: DEFAULT_TENANT_ID,
            nombre: DEFAULT_TENANT_NAME,
            ruc: DEFAULT_TENANT_RUC
        }
    });

    // Ensure User
    const userId = '00000000-0000-0000-0000-000000000001';
    await prisma.usuario.upsert({
        where: { id: userId },
        update: {},
        create: {
            id: userId,
            empresa_id: DEFAULT_TENANT_ID,
            username: 'SYSTEM_TEST',
            nombre_completo: 'System Test User',
            email: 'test@system.com',
            password_hash: 'hash_placeholder',
            activo: true
        }
    });

    // 1. Create Data
    const fabName = `FAB_NEU_${Date.now()}`;
    const fab = await fabricanteService.create({ nombre: fabName, codigoAbreviado: `FN${Date.now().toString().slice(-4)}` });
    if (!fab.success) throw new Error('Fab failed');

    const modName = `MOD_NEU_${Date.now()}`;
    const modelo = await modeloNeumaticoService.create({
        fabricante_id: fab.data.id,
        nombre: modName,
        medida: '11R22.5',
        profundidad_original_mm: 20
    });
    if (!modelo.success) throw new Error('Model failed');

    try {
        // 2. Create Neumatico
        console.log('\n2. Creating Neumatico (Purchase)...');
        const createResult = await neumaticoService.create({
            modelo_id: modelo.data.id,
            // No Serial (test auto-id or empty? Validator says optional)
            numero_serie: `SERIE_${Date.now()}`,
            dot: '4023',
            fecha_compra: new Date().toISOString(),
            profundidad_actual_mm: 20,
            costo_compra: 1500,
            moneda_compra: 'PEN'
        }, DEFAULT_TENANT_ID, userId);

        if (!createResult.success) {
            console.error('❌ Creation failed:', createResult.error);
            process.exit(1);
        }
        const neuId = createResult.data.id;
        console.log('✅ Created:', createResult.data);

        // Verify Event Generation
        const events = await prisma.eventoNeumatico.findMany({ where: { neumatico_id: neuId } });
        if (events.length > 0 && events[0].tipo_evento === 'COMPRA') {
            console.log('✅ Purchase Event created');
        } else {
            console.error('❌ Purchase Event missing');
        }

        // 3. Get All w/ Filter
        console.log('\n3. Listing...');
        const list = await neumaticoService.getAll(DEFAULT_TENANT_ID, { numero_serie: createResult.data.numeroSerie! });
        if (list.success && list.data.length === 1) console.log('✅ Found by filter');
        else console.error('❌ Filter logic failed');

        // 4. Update
        console.log('\n4. Updating...');
        const updateResult = await neumaticoService.update(DEFAULT_TENANT_ID, neuId, {
            dot: '5023'
        }, userId);
        if (updateResult.success && updateResult.data.dot === '5023') {
            console.log('✅ Updated:', updateResult.data.dot);
        }
        // 5. Lifecycle Event: Inspection
        console.log('\n5. Testing Lifecycle (Inspection)...');
        // Inspection changes depth and pressure
        const inspectResult = await neumaticoService.registrarEvento({
            tipo_evento: 'INSPECCION',
            neumatico_id: neuId,
            fecha_evento: new Date().toISOString(),
            profundidad_remanente: 18.5,
            presion_psi: 105,
            observaciones: 'Inspection Test'
        }, userId, DEFAULT_TENANT_ID);

        // Re-fetch to verify updates
        const inspected = await neumaticoService.getById(DEFAULT_TENANT_ID, neuId);
        if (inspected.success && inspected.data.mediciones.profundidadActual === 18.5) {
            console.log('✅ Lifecycle Update Verified (Depth: 18.5)');
        } else {
            console.error('❌ Lifecycle Update Failed:', inspected);
        }

        // 6. Delete
        console.log('\n6. Deleting...');
        const delResult = await neumaticoService.delete(DEFAULT_TENANT_ID, neuId);
        if (delResult.success) console.log('✅ Deleted');
        else console.error('❌ Delete failed');

        // Cleanup dependencies first
        console.log('Cleaning up relations...');
        await prisma.alerta.deleteMany({ where: { neumatico_id: neuId } });
        await prisma.lecturaPresion.deleteMany({ where: { neumatico_id: neuId } });
        await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: neuId } });
        await prisma.medicionProfundidad.deleteMany({ where: { neumatico_id: neuId } });
        await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: neuId } });

        await prisma.neumatico.delete({ where: { id: neuId } });

    } catch (e) {
        console.error(e);
    } finally {
        // Cleanup Deps
        await prisma.modeloNeumatico.delete({ where: { id: modelo.data.id } });
        await prisma.fabricanteNeumatico.delete({ where: { id: fab.data.id } });
        // Keep tenant
        console.log('\n✅ Cleanup complete.');
    }
}

main();
