import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    console.log('🔍 INICIANDO VERIFICACIÓN DE ESTADO DE BASE DE DATOS...\n');

    // 1. Verificar Webhooks y Jobs
    try {
        console.log('--- 1. WEBHOOKS SYSTEM ---');
        const webhooks = await prisma.webhookConfig.findMany({
            include: {
                jobs: { take: 5, orderBy: { created_at: 'desc' } },
                logs: { take: 2, orderBy: { created_at: 'desc' } }
            }
        });
        console.log(`✅ Webhooks Configurados: ${webhooks.length}`);
        webhooks.forEach(w => {
            console.log(`   - ID: ${w.id.substring(0, 8)}... | URL: ${w.url}`);
            console.log(`     - Jobs Encolados/Procesados: ${w.jobs.length} (mostrando últimos 5)`);
            w.jobs.forEach(j => console.log(`       * [${j.status}] ${j.event_type} - Intentos: ${j.attempts}`));
        });
    } catch (e: any) { console.error('Error Webhooks:', e.message); }

    // 2. Verificar Lecturas de Presión
    try {
        console.log('\n--- 2. LECTURAS DE PRESIÓN (Historial chart) ---');
        const lecturasCount = await prisma.lecturaPresion.count();
        console.log(`✅ Total Lecturas de Presión: ${lecturasCount}`);

        const ultimaLectura = await prisma.lecturaPresion.findFirst({
            orderBy: { fecha_lectura: 'desc' },
            include: { neumatico: { select: { numero_serie: true } } }
        });

        if (ultimaLectura) {
            console.log(`   - Última lectura: ${ultimaLectura.presion_psi} PSI en Neumático ${ultimaLectura.neumatico?.numero_serie}`);
            console.log(`   - Fecha: ${ultimaLectura.fecha_lectura.toISOString()}`);
        } else {
            console.log('   ⚠️ No hay lecturas registradas aún (Gráficos estarán vacíos)');
        }
    } catch (e: any) { console.error('Error Lecturas:', e.message); }

    // 3. Verificar Alertas
    try {
        console.log('\n--- 3. ALERTAS ACTIVAS ---');
        // @ts-ignore: Enum strictness
        const alertasCriticas = await prisma.alerta.findMany({
            where: { severidad: 'CRITICAL', estado: 'PENDIENTE' },
            take: 5
        });
        console.log(`✅ Alertas Críticas Pendientes: ${alertasCriticas.length}`);
        alertasCriticas.forEach(a => {
            console.log(`   - [${a.tipo}] ${a.mensaje} (Neumático: ${a.neumatico_id ? a.neumatico_id.substring(0, 8) : 'N/A'}...)`);
        });
    } catch (e: any) { console.error('Error Alertas:', e.message); }

    // 4. Verificar Neumáticos (Core integrity)
    try {
        console.log('\n--- 4. INVENTARIO CORE ---');
        const neumaticosCount = await prisma.neumatico.count();
        // @ts-ignore: Enum strictness
        const enUsoCount = await prisma.neumatico.count({ where: { estado_actual: 'EN_USO' } });
        console.log(`✅ Total Neumáticos: ${neumaticosCount}`);
        console.log(`   - En Uso (Instalados): ${enUsoCount}`);
        console.log(`   - En Stock/Otros: ${neumaticosCount - enUsoCount}`);
    } catch (e: any) { console.error('Error Inventario:', e.message); }

}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
