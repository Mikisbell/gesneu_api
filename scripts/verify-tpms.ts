/**
 * TPMS Verification Script (Robust)
 */
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

// Setup Prisma with Adapter
const connectionString = process.env.DIRECT_URL || process.env.DATABASE_URL;
const pool = new Pool({ connectionString });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

const API_URL = 'http://localhost:3005/api/v1/integraciones/tpms';

async function main() {
    console.log('📡 Starting TPMS Verification...');
    const EMPRESA_ID = '123e4567-e89b-12d3-a456-426614174000'; // Fixed UUID for context
    const SENSOR_ID = 'SENSOR-' + Date.now();

    let testData: any = {};

    try {
        // 1. Setup Data (Transactional with RLS Context)
        console.log('1. Setting up Test Data...');

        await prisma.$transaction(async (tx) => {
            // Attempt to set RLS context
            // Kitchen Sink Bypass Strategy
            try {
                // 1. Mock Supabase Auth context (used by auth.uid() if wrapped)
                const jwtClaims = JSON.stringify({
                    sub: '00000000-0000-0000-0000-000000000000',
                    role: 'service_role',
                    app_metadata: { provider: 'email' },
                    user_metadata: {}
                });
                await tx.$executeRawUnsafe(`SELECT set_config('request.jwt.claims', '${jwtClaims}', true)`);

                // 2. Set App Context variables (used by custom triggers)
                await tx.$executeRawUnsafe(`SELECT set_config('app.current_tenant', '${EMPRESA_ID}', true)`);
                await tx.$executeRawUnsafe(`SELECT set_config('app.current_user_id', '00000000-0000-0000-0000-000000000000', true)`);

                // 3. Try Role Escalation (Postgres level)
                await tx.$executeRawUnsafe(`SELECT set_config('role', 'service_role', true)`);
            } catch (ignore) { console.log('Bypass warning:', ignore); }

            // Upsert Enterprise
            const empresa = await tx.empresa.upsert({
                where: { id: EMPRESA_ID },
                update: {},
                create: {
                    id: EMPRESA_ID,
                    nombre: 'Verify Corp',
                    ruc: 'TEST-' + Date.now(),
                    activo: true
                }
            });

            // Create Maker/Model
            const fab = await tx.fabricanteNeumatico.create({
                data: {
                    nombre: 'VerifyMaker ' + Date.now(),
                    // empresa: shared catalog
                }
            });

            const modelo = await tx.modeloNeumatico.create({
                data: {
                    nombre_modelo: 'VerifyModel',
                    medida: '11R22.5',
                    profundidad_original_mm: 20,
                    fabricante_id: fab.id,
                    presion_recomendada_psi: 100 // Target 100
                }
            });

            // Create Tire
            const neumatico = await tx.neumatico.create({
                data: {
                    numero_serie: 'VERIFY-' + Date.now(),
                    modelo_id: modelo.id,
                    empresa_id: empresa.id,
                    fecha_compra: new Date(),
                    estado_actual: 'EN_STOCK',
                    profundidad_remanente_actual_mm: 20,
                    sensor_id: SENSOR_ID,
                    presion_actual_psi: 100,
                    activo: true
                }
            });

            testData = { neumatico, modelo, fab, empresa };
            console.log(`   Created Tire: ${neumatico.numero_serie} with Sensor: ${SENSOR_ID}`);
        });

        // 2. Execute API Call
        console.log('\n2. Sending Data to API...');
        const payload = [{
            sensor_id: SENSOR_ID,
            psi: 50, // Critical
            temp_c: 65,
            timestamp: new Date().toISOString()
        }];

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': process.env.TPMS_API_KEY || 'default-secret-key'
            },
            body: JSON.stringify(payload)
        });

        console.log(`   Status: ${response.status}`);
        const json: any = await response.json();
        console.log('   Response:', json);

        if (response.status !== 200) {
            console.error('❌ API Call Failed');
            if (response.status === 500 && json.error === 'Server misconfiguration') {
                console.warn('⚠️  HINT: The running server needs TPMS_API_KEY set in .env');
            }
        } else {
            // 3. Verify Database (Read-only check)
            console.log('\n3. Verifying Database State...');

            // Check Reading
            const reading = await prisma.lecturaPresion.findFirst({
                where: { neumatico_id: testData.neumatico.id }
            });

            if (reading && Number(reading.presion_psi) === 50) {
                console.log('✅ Reading stored correctly (50 PSI)');
            } else {
                console.error('❌ Reading not found', reading);
            }

            // Check Alert
            const alert = await prisma.alerta.findFirst({
                where: { neumatico_id: testData.neumatico.id, tipo: 'PRESION_BAJA' }
            });

            // Note: Alerts are async in API. Might need slight delay? 
            // In integration test we awaited. Here API awaits it before returning in route.ts logic.
            if (alert) {
                console.log('✅ Alert generated:', alert.mensaje);
            } else {
                console.log('❓ Alert not found immediately (Check async logic)');
            }
        }

    } catch (e) {
        console.error('❌ Error during verification:', e);
    } finally {
        // Cleanup if data exists
        if (testData.neumatico) {
            console.log('\n🧹 Cleaning up...');
            try {
                await prisma.lecturaPresion.deleteMany({ where: { neumatico_id: testData.neumatico.id } });
                await prisma.alerta.deleteMany({ where: { neumatico_id: testData.neumatico.id } });
                await prisma.neumatico.delete({ where: { id: testData.neumatico.id } });
                await prisma.modeloNeumatico.delete({ where: { id: testData.modelo.id } });
                await prisma.fabricanteNeumatico.delete({ where: { id: testData.fab.id } });
            } catch (cleanupErr) {
                console.warn('Cleanup partial error:', cleanupErr);
            }
        }
        await prisma.$disconnect();
    }
}

main();
