
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
    console.log('--- VERIFICANDO HARDENING DE BASE DE DATOS ---');

    // 1. Preparar datos dependientes
    const fabricante = await prisma.fabricanteNeumatico.create({
        data: { nombre: 'TEST_FAB_HARDENING_' + Date.now() }
    });

    const modelo = await prisma.modeloNeumatico.create({
        data: {
            nombre: 'TEST_MODEL_HARDENING',
            medida: '11R22.5',
            profundidad_inicial_mm: 20,
            fabricante_id: fabricante.id
        }
    });

    // 2. Test: Presión Negativa
    console.log('\n[TEST 1] Intentando insertar neumático con Presión -10 PSI...');
    try {
        await prisma.neumatico.create({
            data: {
                numero_serie: 'NS-' + Date.now(),
                modelo_id: modelo.id,
                profundidad_inicial_mm: 20,
                presion_actual_psi: -10 // INVALID
            }
        });
        console.log('❌ FAIL: Se permitió presión negativa.');
    } catch (e: any) {
        if (e.message.includes('check_neumatico_presion_positiva')) {
            console.log('✅ SUCCESS: Bloqueado por check_neumatico_presion_positiva');
        } else {
            console.log('⚠️ ERROR INESPERADO:', e.message);
        }
    }

    // 3. Test: Profundidad Actual > Inicial
    console.log('\n[TEST 2] Intentando insertar neumático con Profundidad 25mm (Inicial 20mm)...');
    try {
        await prisma.neumatico.create({
            data: {
                numero_serie: 'NS2-' + Date.now(),
                modelo_id: modelo.id,
                profundidad_inicial_mm: 20,
                profundidad_actual_mm: 25 // INVALID
            }
        });
        console.log('❌ FAIL: Se permitió crecimiento mágico de caucho.');
    } catch (e: any) {
        if (e.message.includes('check_neumatico_desgaste_logico')) {
            console.log('✅ SUCCESS: Bloqueado por check_neumatico_desgaste_logico');
        } else {
            console.log('⚠️ ERROR INESPERADO:', e.message);
        }
    }

    // 4. Test: Reencauches Negativos
    console.log('\n[TEST 3] Intentando insertar reencauches -1...');
    try {
        await prisma.neumatico.create({
            data: {
                numero_serie: 'NS3-' + Date.now(),
                modelo_id: modelo.id,
                profundidad_inicial_mm: 20,
                reencauches_realizados: -1 // INVALID
            }
        });
        console.log('❌ FAIL: Se permitió reencauches negativos.');
    } catch (e: any) {
        if (e.message.includes('check_neumatico_reencauches_positivos')) {
            console.log('✅ SUCCESS: Bloqueado por check_neumatico_reencauches_positivos');
        } else {
            console.log('⚠️ ERROR INESPERADO:', e.message);
        }
    }

    // Limpieza
    await prisma.modeloNeumatico.delete({ where: { id: modelo.id } });
    await prisma.fabricanteNeumatico.delete({ where: { id: fabricante.id } });
    console.log('\n--- VERIFICACIÓN COMPLETADA ---');
}

main()
    .catch(console.error)
    .finally(async () => await prisma.$disconnect())
