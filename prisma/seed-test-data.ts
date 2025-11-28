import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

const randomFromArray = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

async function main() {
    console.log('🌱 [SEED] Starting...\n');

    // Clean
    console.log('🧹 [SEED] Cleaning...');
    await prisma.eventoNeumatico.deleteMany();
    await prisma.neumatico.deleteMany();
    await prisma.vehiculo.deleteMany();
    await prisma.modeloNeumatico.deleteMany();
    await prisma.fabricanteNeumatico.deleteMany();
    await prisma.almacen.deleteMany();
    await prisma.proveedor.deleteMany();

    // 1. Proveedores
    console.log('📦 [SEED] Creating 50 proveedores...');
    const proveedores = [];
    const tiposProveedor = ['FABRICANTE', 'DISTRIBUIDOR', 'SERVICIO_REPARACION', 'SERVICIO_REENCAUCHE'];
    for (let i = 1; i <= 50; i++) {
        proveedores.push(await prisma.proveedor.create({
            data: {
                tipo: randomFromArray(tiposProveedor) as any,
                nombre: `Proveedor ${i}`,
                ruc: `2010${String(i).padStart(6, '0')}1`,
                contacto_principal: `Contact ${i}`,
                telefono: `+1-555-${String(i).padStart(4, '0')}`,
                email: `prov${i}@example.com`,
                direccion: `Address ${i}`,
            }
        }));
    }

    // 2. Almacenes
    console.log('🏭 [SEED] Creating 50 almacenes...');
    const almacenes = [];
    for (let i = 1; i <= 50; i++) {
        almacenes.push(await prisma.almacen.create({
            data: {
                codigo: `ALM${String(i).padStart(3, '0')}`,
                nombre: `Almacén ${i}`,
                ubicacion: `Zone ${String.fromCharCode(65 + (i % 26))}`,
                descripcion: `Warehouse ${i}`,
            }
        }));
    }

    // 3. Fabricantes
    console.log('🏭 [SEED] Creating fabric antes...');
    const fabricanteNames = ['Michelin', 'Bridgestone', 'Goodyear', 'Continental', 'Pirelli',
        'Yokohama', 'Hankook', 'Cooper', 'Dunlop', 'Firestone'];
    const fabricantes = [];
    for (const name of fabricanteNames) {
        fabricantes.push(await prisma.fabricanteNeumatico.create({
            data: {
                nombre: name,
                pais_origen: randomFromArray(['USA', 'Japan', 'Germany', 'France', 'Italy']),
            }
        }));
    }

    // 4. Modelos
    console.log('🛞 [SEED] Creating 100 modelos...');
    const modelos = [];
    const medidas = ['295/80R22.5', '315/80R22.5', '385/65R22.5', '445/65R22.5'];
    const tipos = ['DIRECCION', 'TRACCION', 'ARRASTRE'];

    for (let i = 1; i <= 100; i++) {
        modelos.push(await prisma.modeloNeumatico.create({
            data: {
                nombre: `Model ${i}`,
                fabricante_id: randomFromArray(fabricantes).id,
                medida: randomFromArray(medidas),
                profundidad_inicial_mm: randomInt(15, 22),
                indice_carga: String(randomInt(140, 160)),
                indice_velocidad: randomFromArray(['J', 'K', 'L']),
                vida_util_km: randomInt(80000, 150000),
            }
        }));
    }

    // 5. Vehículos
    console.log('🚛 [SEED] Creating 60 vehículos...');
    const vehiculos = [];
    const marcas = ['Volvo', 'Scania', 'Mercedes-Benz', 'MAN', 'DAF'];
    const estados = ['ACTIVO', 'EN_MANTENIMIENTO', 'FUERA_DE_SERVICIO'];

    for (let i = 1; i <= 60; i++) {
        vehiculos.push(await prisma.vehiculo.create({
            data: {
                placa: `ABC${String(i).padStart(3, '0')}`,
                marca: randomFromArray(marcas),
                modelo: `Model ${randomInt(2015, 2024)}`,
                anio_fabricacion: randomInt(2015, 2024),
                tipo_vehiculo: randomFromArray(['TRACTO', 'RIGIDO']),
                numero_ejes: randomInt(2, 4),
                kilometraje_actual: randomInt(50000, 500000),
                estado: randomFromArray(estados) as any,
            }
        }));
    }

    // 6. Neumáticos
    console.log('🛞 [SEED] Creating 200 neumáticos...');
    const neumaticos = [];
    const estados_neumatico = ['NUEVO', 'USADO_BUENO', 'USADO_REGULAR', 'REENCAUCHADO'];

    for (let i = 1; i <= 200; i++) {
        const estado = randomFromArray(estados_neumatico);
        const enAlmacen = Math.random() > 0.4;

        neumaticos.push(await prisma.neumatico.create({
            data: {
                numero_serie: `NS${String(i).padStart(6, '0')}`,
                modelo_id: randomFromArray(modelos).id,
                dot: `${randomInt(1, 52)}${randomInt(15, 24)}`,
                estado_actual: estado as any,
                profundidad_actual_mm: randomInt(5, 20),
                presion_actual_psi: randomInt(90, 120),
                kilometraje_actual: estado === 'NUEVO' ? 0 : randomInt(10000, 100000),
                ubicacion_almacen_id: enAlmacen ? randomFromArray(almacenes).id : null,
                ubicacion_vehiculo_id: !enAlmacen && Math.random() > 0.3 ? randomFromArray(vehiculos).id : null,
                ubicacion_posicion: !enAlmacen && Math.random() > 0.3 ? randomFromArray(['EJE1_IZQ', 'EJE1_DER', 'EJE2_IZQ_EXT']) : null,
            }
        }));
    }

    console.log('\n✅ [SEED] Completed!\n');
    console.log(`  - Proveedores: ${proveedores.length}`);
    console.log(`  - Almacenes: ${almacenes.length}`);
    console.log(`  - Fabricantes: ${fabricantes.length}`);
    console.log(`  - Modelos: ${modelos.length}`);
    console.log(`  - Vehículos: ${vehiculos.length}`);
    console.log(`  - Neumáticos: ${neumaticos.length}\n`);
}

main()
    .catch((e) => {
        console.error('❌ [SEED] Error:', e.message);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
