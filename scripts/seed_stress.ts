
import 'dotenv/config';
import { PrismaClient, EstadoNeumaticoEnum, TipoEjeEnum, LadoVehiculoEnum, TipoProveedorEnum, Prisma } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

// --- CONFIGURACIÓN DE CONEXIÓN (DRIVER ADAPTER) ---
const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    max: 20 // Mayor concurrencia para seeding
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

// --- HELPERS ---
const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomFloat = (min: number, max: number) => parseFloat((Math.random() * (max - min) + min).toFixed(2));
const pickRequest = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

async function main() {
    console.log('🌱 INICIANDO SEEDING DE ESTRÉS (Enterprise v2)...');

    // 1. Obtener datos base
    const almacenes = await prisma.almacen.findMany();
    if (almacenes.length === 0) {
        console.error('❌ No hay almacenes. Ejecuta el seed base primero o crea uno manual.');
        return;
    }
    const almacenCentral = almacenes.find(a => a.tipo === 'PRINCIPAL') || almacenes[0];

    // 1.5 Obtener Empresa Default
    const empresa = await prisma.empresa.findFirst();
    if (!empresa) {
        console.error('❌ No hay empresa default. Ejecuta prisma/seed.ts primero.');
        process.exit(1);
    }

    // 2. Crear/Identificar Fabricantes y Modelos
    const fabricantes = ['MICHELIN', 'BRIDGESTONE', 'GOODYEAR', 'CONTINENTAL', 'PIRELLI'];
    const modelosData = [
        { nombre: 'X MULTI Z', medida: '295/80R22.5', prof: 16.0 },
        { nombre: 'R268 ECOPIA', medida: '11R22.5', prof: 15.5 },
        { nombre: 'KMAX S', medida: '295/80R22.5', prof: 15.8 },
        { nombre: 'HSR2', medida: '11R22.5', prof: 16.2 }
    ];

    const modelosIds: string[] = [];

    console.log('🏭 Verificando Fabricantes y Modelos...');
    for (const fabName of fabricantes) {
        const codigo = fabName.substring(0, 3);
        const fab = await prisma.fabricanteNeumatico.upsert({
            where: { codigo_abreviado: codigo },
            update: {},
            create: { nombre: fabName, codigo_abreviado: codigo }
        });

        // Crear modelos para este fabricante
        for (const modData of modelosData) {
            const mod = await prisma.modeloNeumatico.upsert({
                where: {
                    fabricante_id_nombre_modelo_medida: {
                        fabricante_id: fab.id,
                        nombre_modelo: `${modData.nombre} ${fab.codigo_abreviado}`,
                        medida: modData.medida
                    }
                },
                update: {},
                create: {
                    nombre_modelo: `${modData.nombre} ${fab.codigo_abreviado}`,
                    medida: modData.medida,
                    profundidad_original_mm: modData.prof,
                    fabricante_id: fab.id,
                    vida_util_teorica_km: 120000,
                    indice_carga: '152',
                    indice_velocidad: 'M'
                }
            });
            modelosIds.push(mod.id);
        }
    }

    // 3. Poblar Vehículos (Montar Neumáticos)
    console.log('🚗 Consultando vehículos...');
    const vehiculos = await prisma.vehiculo.findMany({
        include: {
            tipo_vehiculo: {
                include: {
                    configuraciones: {
                        include: { posiciones: true }
                    }
                }
            },
            neumaticos_instalados: true
        }
    });

    console.log(`📋 Procesando ${vehiculos.length} vehículos...`);
    let neumaticosCreados = 0;

    for (const v of vehiculos) {
        // Solo procesar si tiene configuraciones y no está lleno (simple check)
        if (!v.tipo_vehiculo || v.neumaticos_instalados.length > 0) continue;

        const configEjes = v.tipo_vehiculo.configuraciones;

        for (const eje of configEjes) {
            for (const pos of eje.posiciones) {
                // Crear neumático instalado
                const modeloId = pickRequest(modelosIds);
                const serie = `SEED-${v.placa}-${pos.codigo_posicion}-${randomInt(100, 999)}`;

                // Simular desgaste aleatorio
                const kmAcum = randomInt(5000, 80000);
                const profOriginal = 16.0; // Simplificado
                const desgaste = (kmAcum / 120000) * (profOriginal - 2); // Lineal simple
                const profActual = Math.max(2, profOriginal - desgaste);

                await prisma.neumatico.create({
                    data: {
                        numero_serie: serie,
                        modelo_id: modeloId,
                        dot: `${randomInt(10, 52)}${randomInt(20, 24)}`,
                        estado_actual: EstadoNeumaticoEnum.INSTALADO,
                        profundidad_inicial_mm: profOriginal,
                        profundidad_remanente_actual_mm: profActual,
                        presion_actual_psi: 110, // Estándar
                        ubicacion_vehiculo_id: v.id,
                        ubicacion_posicion_id: pos.id,
                        kilometraje_acumulado: kmAcum,
                        fecha_compra: new Date(Date.now() - randomInt(366, 730) * 24 * 60 * 60 * 1000), // Compra anterior
                        costo_compra: 450.00,
                        empresa_id: empresa.id,
                        version: 0
                    }
                });
                neumaticosCreados++;
            }
        }
        process.stdout.write('.'); // Progress indicator
    }
    console.log(`\n✅ Montados ${neumaticosCreados} neumáticos en flota.`);

    // 4. Inventario de Stock (Nuevos)
    console.log('📦 Generando Stock de Almacén...');
    const stockQty = 200;
    for (let i = 0; i < stockQty; i++) {
        const modeloId = pickRequest(modelosIds);
        await prisma.neumatico.create({
            data: {
                numero_serie: `STOCK-${randomInt(10000, 99999)}`,
                modelo_id: modeloId,
                dot: '4524',
                estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                profundidad_inicial_mm: 16.0,
                profundidad_remanente_actual_mm: 16.0,
                ubicacion_almacen_id: almacenCentral.id,
                costo_compra: randomFloat(400, 600),
                fecha_compra: new Date(),
                empresa_id: empresa.id,
                version: 0
            }
        });
    }
    console.log(`✅ Creados ${stockQty} neumáticos en stock.`);

    console.log('✨ SEEDING DE ESTRÉS COMPLETADO ✨');
}

main()
    .catch(e => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
