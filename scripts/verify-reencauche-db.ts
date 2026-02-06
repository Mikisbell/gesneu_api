import { prisma } from '../src/lib/prisma';
import { ReencaucheService } from '../src/lib/services/reencauche.service';
import { EstadoNeumaticoEnum } from '@prisma/client';

async function main() {
    console.log("🧪 INICIO DE PRUEBA DE REENCAUCHE (Backend & DB Check)...");

    // 1. Setup
    const service = new ReencaucheService();
    const empresa = await prisma.empresa.findFirst() || await prisma.empresa.create({ data: { nombre: 'Test Corp', ruc: '99999999999' } });
    const almacen = await prisma.almacen.findFirst({ where: { empresa_id: empresa.id } }) || await prisma.almacen.create({ data: { nombre: 'Almacen Main', codigo: 'MAIN', empresa_id: empresa.id } });
    const modelo = await prisma.modeloNeumatico.findFirst() || await prisma.modeloNeumatico.create({
        data: {
            nombre_modelo: 'XZE',
            medida: '11R22.5',
            fabricante_id: (await prisma.fabricanteNeumatico.findFirst())?.id || (await prisma.fabricanteNeumatico.create({ data: { nombre: 'Mich' } })).id,
            profundidad_original_mm: 20
        }
    });

    // 1.1 Setup Proveedor
    const proveedor = await prisma.proveedor.findFirst({ where: { empresa_id: empresa.id } }) || await prisma.proveedor.create({
        data: {
            nombre: 'Renovadora del Sur',
            empresa_id: empresa.id,
            tipo: 'SERVICIO_REENCAUCHE',
            ruc: '20' + Date.now().toString().slice(0, 9)
        }
    });



    // 1.2 Setup Usuario
    const user = await prisma.usuario.findFirst({ where: { empresa_id: empresa.id } }) || await prisma.usuario.create({
        data: {
            username: 'testuser',
            email: 'test@test.com',
            password_hash: 'hash',
            nombre_completo: 'Test User',
            empresa_id: empresa.id,
            rol: 'ADMIN'
        }
    });

    // 2. Crear Neumático (Vida 1)
    const serie = `VERIFY-${Date.now()}`;
    console.log(`\n📌 1. CREANDO NEUMÁTICO: ${serie}`);
    const tire = await prisma.neumatico.create({
        data: {
            numero_serie: serie,
            empresa_id: empresa.id,
            modelo_id: modelo.id,
            estado_actual: EstadoNeumaticoEnum.EN_ALMACEN,
            vida_actual: 1,
            reencauches_realizados: 0,
            profundidad_remanente_actual_mm: 3, // Desgastado
            kilometraje_vida_actual: 50000,
            ubicacion_almacen_id: almacen.id,
            fecha_compra: new Date()
        }
    });
    console.log(`   ✅ Creado. Vida: ${tire.vida_actual}, Prof: ${tire.profundidad_remanente_actual_mm}mm`);

    // 3. Enviar a Reencauche
    console.log(`\n🚚 2. ENVIANDO A PLANTA...`);
    await service.registrarEnvio(tire.id, proveedor.id, user.id, empresa.id);

    // DB CHECK 1
    const tireSent = await prisma.neumatico.findUnique({ where: { id: tire.id } });
    console.log(`   🔎 DB CHECK: Estado es ${tireSent?.estado_actual} (Esperado: EN_REENCAUCHE)`);

    // 4. Retornar de Reencauche
    console.log(`\n🏭 3. RETORNANDO DE PLANTA (NUEVA VIDA)...`);
    await service.registrarRetorno(
        tire.id,
        {
            profundidad_nueva: 18.0,
            proveedor_id: proveedor.id,
            costo: 120,
            almacen_destino_id: almacen.id
        },
        user.id,
        empresa.id
    );

    // DB CHECK 2
    const tireReturned = await prisma.neumatico.findUnique({ where: { id: tire.id } });
    console.log(`\n📊 RESULTADOS FINALES (DB STATE):`);
    console.log(`   ----------------------------------------`);
    console.log(`   Vida Actual:       ${tireReturned?.vida_actual}      (Esperado: 2)`);
    console.log(`   Nº Reencauches:    ${tireReturned?.reencauches_realizados}      (Esperado: 1)`);
    console.log(`   KM Vida Actual:    ${tireReturned?.kilometraje_vida_actual}      (Esperado: 0)`);
    console.log(`   Profundidad:       ${tireReturned?.profundidad_remanente_actual_mm}mm   (Esperado: 18)`);
    console.log(`   Es Reencauchado:   ${tireReturned?.es_reencauchado}   (Esperado: true)`);
    console.log(`   ----------------------------------------`);

    if (tireReturned?.vida_actual === 2 && tireReturned?.kilometraje_vida_actual?.toString() === '0') {
        console.log("✅✅ PRUEBA EXITOSA: El Sistema de Reencauche funciona correctamente.");
    } else {
        console.error("❌❌ PRUEBA FALLIDA: Los datos no coinciden.");
        process.exit(1);
    }
}

main().catch(e => {
    console.error(e);
    process.exit(1);
});
