const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

(async () => {
    // Test 1: CentroCosto
    console.log('=== CentroCosto ===');
    try {
        const cc = await prisma.centroCosto.create({
            data: { empresa_id: '00000000-0000-0000-0000-000000000000', codigo: 'TEST-CC-' + Date.now(), nombre: 'Test CC', area_negocio: 'Test', activo: true }
        });
        console.log('OK:', cc.id);
    } catch (e) {
        console.log('ERR:', e.message, 'code:', e.code);
    }

    // Test 2: TareaProgramada
    console.log('\n=== TareaProgramada ===');
    try {
        const t = await prisma.tareaProgramada.create({
            data: { nombre: 'Test', tipo: 'GENERAR_REPORTE', cron_expresion: '0 8 * * 1', activo: true, parametros: { formato: 'pdf' } }
        });
        console.log('OK:', t.id);
    } catch (e) {
        console.log('ERR:', e.message, 'code:', e.code);
    }

    // Test 3: Check existing CentroCosto records
    console.log('\n=== CentroCosto count ===');
    try {
        const count = await prisma.centroCosto.count();
        console.log('Count:', count);
    } catch (e) {
        console.log('ERR:', e.message);
    }

    await prisma.$disconnect();
})();
