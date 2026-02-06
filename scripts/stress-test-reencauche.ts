import 'dotenv/config';
import { prisma } from '../src/lib/prisma';
import { ReencaucheService } from '../src/lib/services/reencauche.service';
import { EstadoNeumaticoEnum } from '@prisma/client';
import { EventBus } from '../src/lib/events/core'; // Force import

const CONCURRENCY = 20;

async function main() {
    console.log(`🔥 INICIANDO PRUEBA DE ESTRÉS: REENCAUCHE (${CONCURRENCY} ciclos concurrentes)`);
    const service = new ReencaucheService();

    // 1. Setup Data
    console.log("1. Preparando datos maestros...");
    const empresa = await prisma.empresa.findFirst() || await prisma.empresa.create({ data: { nombre: 'Stress Corp', ruc: '99999999998' } });
    const almacen = await prisma.almacen.findFirst({ where: { empresa_id: empresa.id } }) || await prisma.almacen.create({ data: { nombre: 'Almacen Stress', codigo: 'STR', empresa_id: empresa.id } });
    const proveedor = await prisma.proveedor.findFirst({ where: { empresa_id: empresa.id } }) || await prisma.proveedor.create({ data: { nombre: 'Renovadora Stress', tipo: 'SERVICIO_REENCAUCHE', empresa_id: empresa.id } });
    const modelo = await prisma.modeloNeumatico.findFirst();
    const user = await prisma.usuario.findFirst({ where: { empresa_id: empresa.id } }) || await prisma.usuario.create({ data: { username: 'stress', email: 's@s.com', password_hash: 'x', nombre_completo: 'Stress', empresa_id: empresa.id, rol: 'ADMIN' } });

    if (!modelo) throw new Error("No model found");

    // 2. Create Bulk Tires
    console.log(`2. Creando ${CONCURRENCY} neumáticos...`);
    const tires = [];
    for (let i = 0; i < CONCURRENCY; i++) {
        tires.push(await prisma.neumatico.create({
            data: {
                numero_serie: `STRESS-${Date.now()}-${i}`,
                empresa_id: empresa.id,
                modelo_id: modelo.id,
                estado_actual: EstadoNeumaticoEnum.EN_ALMACEN,
                vida_actual: 1,
                reencauches_realizados: 0,
                profundidad_remanente_actual_mm: 2,
                ubicacion_almacen_id: almacen.id,
                fecha_compra: new Date()
            }
        }));
    }
    console.log("   ✅ Neumáticos creados.");

    // 3. Concurrent Send (Setup - Serialized to prevent connection exhaustion before the real test)
    console.log("3. Ejecutando ENVÍOS (Setup Sequential)...");
    const startSend = Date.now();

    // Chunked execution for setup
    for (const t of tires) {
        try {
            await service.registrarEnvio(t.id, proveedor.id, user.id, empresa.id);
        } catch (e) {
            console.error(`❌ Falló envio setup ${t.numero_serie}:`, e.message);
        }
    }
    const endSend = Date.now();
    console.log(`   ⏱️  Envío completado en ${(endSend - startSend) / 1000}s`);

    // Verify State
    const countEnReencauche = await prisma.neumatico.count({
        where: { id: { in: tires.map(t => t.id) }, estado_actual: 'EN_REENCAUCHE' }
    });
    console.log(`   🔎 Estado Check: ${countEnReencauche}/${CONCURRENCY} en REENCAUCHE.`);

    // 4. Concurrent Return (The Transaction Test)
    console.log("4. Ejecutando RETORNOS masivos (Transaction Locking Test)...");
    const startRet = Date.now();

    // We Map results to check individual success
    const results = await Promise.allSettled(tires.map(t =>
        service.registrarRetorno(
            t.id,
            {
                profundidad_nueva: 18,
                proveedor_id: proveedor.id,
                costo: 100,
                almacen_destino_id: almacen.id
            },
            user.id,
            empresa.id
        )
    ));
    const endRet = Date.now();

    // 5. Analysis
    const successes = results.filter(r => r.status === 'fulfilled').length;
    const failures = results.filter(r => r.status === 'rejected').length;

    console.log(`\n📊 RESULTADOS DE ESTRÉS:`);
    console.log(`   Total Intentos:    ${CONCURRENCY}`);
    console.log(`   Éxitos:            ${successes} ✅`);
    console.log(`   Fallos:            ${failures} ❌`);
    console.log(`   Tiempo Total Ret:  ${(endRet - startRet) / 1000}s`);
    console.log(`   TPS (Tx/Sec):      ${(CONCURRENCY / ((endRet - startRet) / 1000)).toFixed(2)}`);

    if (failures > 0) {
        console.log("   ⚠️ Causas de fallo:", results.filter(r => r.status === 'rejected').map(r => (r as any).reason.message).slice(0, 5));
        process.exit(1);
    } else {
        console.log("   🚀 PERFORMANCE ÓPTIMA. Sin condiciones de carrera detectadas.");
    }
}

main()
    .catch(console.error)
    .finally(async () => {
        await prisma.$disconnect();
    });
