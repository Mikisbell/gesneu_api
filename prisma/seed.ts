/**
 * Production Seeder for GesNeu
 * 
 * Creates realistic test data for Sprint 1: Montaje workflow
 * 
 * Data created:
 * - 10 Fabricantes de neumáticos
 * - 20 Tipos de vehículo
 * - 50 Modelos de neumáticos
 * - 50 Almanences
 * - 50 Proveedores
 * - 30 Vehículos
 * - 100 Neumáticos (60% EN_STOCK, 30% INSTALADO, 10% others)
 * 
 * Total: ~260 registros
 */

import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

const random = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomFloat = (min: number, max: number) => Math.random() * (max - min) + min;

async function main() {
    console.log('🌱 [SEED] Iniciando seed de producción...\n');

    // Limpiar datos existentes (opcional - comentar si quieres mantener datos)
    console.log('🧹 [SEED] Limpiando datos existentes...');
    await prisma.eventoNeumatico.deleteMany();
    await prisma.neumatico.deleteMany();
    await prisma.vehiculo.deleteMany();
    await prisma.modeloNeumatico.deleteMany();
    await prisma.fabricanteNeumatico.deleteMany();
    await prisma.tipoVehiculo.deleteMany();
    await prisma.almacen.deleteMany();
    await prisma.proveedor.deleteMany();

    // 1. Fabricantes de Neumáticos
    console.log('🏭 [SEED] Creando 10 fabricantes...');
    const fabricanteNames = [
        'Michelin', 'Bridgestone', 'Goodyear', 'Continental', 'Pirelli',
        'Yokohama', 'Hankook', 'Cooper', 'Dunlop', 'Firestone'
    ];
    const fabricantes = [];
    for (const nombre of fabricanteNames) {
        fabricantes.push(await prisma.fabricanteNeumatico.create({
            data: {
                nombre,
                pais_origen: random(['USA', 'Japan', 'Germany', 'France', 'Italy', 'South Korea']),
            }
        }));
    }

    // 2. Tipos de Vehículo
    console.log('🚛 [SEED] Creando 20 tipos de vehículo...');
    const tiposVehiculo = [];
    const tipoNames = [
        'Tracto 6x4', 'Tracto 4x2', 'Rigido 8x4', 'Rigido 6x4',
        'Minibus', 'Bus Interprovincial', 'Camión Volquete', 'Camión Cisterna',
        'Camión Plataforma', 'Camión Refrigerado', 'Tracto Minero',
        'Camión Mixer', 'Camión Grúa', 'Tracto Porta-Contenedor',
        'Camión Baranda', 'Camión Furgón', 'Camión Tolva', 'Bus Urbano',
        'Tracto Low Boy', 'Camión Compactador'
    ];

    for (const nombre of tipoNames) {
        tiposVehiculo.push(await prisma.tipoVehiculo.create({
            data: {
                nombre,
                descripcion: `Tipo de vehículo ${nombre}`,
            }
        }));
    }

    // 3. Almacenes
    console.log('🏭 [SEED] Creando 50 almacenes...');
    const almacenes = [];
    for (let i = 1; i <= 50; i++) {
        almacenes.push(await prisma.almacen.create({
            data: {
                codigo: `ALM${String(i).padStart(3, '0')}`,
                nombre: `Almacén ${i}`,
                ubicacion: `Zona ${String.fromCharCode(65 + (i % 26))}`,
                descripcion: `Almacén de neumáticos ${i}`,
            }
        }));
    }

    // 4. Proveedores
    console.log('📦 [SEED] Creando 50 proveed ores...');
    const proveedores = [];
    const tiposProveedor = ['FABRICANTE', 'DISTRIBUIDOR', 'SERVICIO_REPARACION', 'SERVICIO_REENCAUCHE'];
    for (let i = 1; i <= 50; i++) {
        proveedores.push(await prisma.proveedor.create({
            data: {
                tipo: random(tiposProveedor) as any,
                nombre: `Proveedor ${i}`,
                ruc: `2010${String(i).padStart(6, '0')}1`,
                contacto_principal: `Contacto ${i}`,
                telefono: `+1-555-${String(i).padStart(4, '0')}`,
                email: `prov${i}@example.com`,
                direccion: `Dirección ${i}, Lima, Perú`,
            }
        }));
    }

    // 5. Modelos de Neumáticos
    console.log('🛞 [SEED] Creando 50 modelos de neumáticos...');
    const modelos = [];
    const medidas = ['295/80R22.5', '315/80R22.5', '385/65R22.5', '445/65R22.5', '11R22.5', '12R22.5'];

    for (let i = 1; i <= 50; i++) {
        modelos.push(await prisma.modeloNeumatico.create({
            data: {
                fabricante_id: random(fabricantes).id,
                nombre: `Modelo ${i}`,
                medida: random(medidas),
                profundidad_inicial_mm: randomFloat(15, 22),
                indice_carga: String(randomInt(140, 160)),
                indice_velocidad: random(['J', 'K', 'L', 'M']),
                vida_util_km: randomInt(80000, 150000),
                reencauches_maximos: randomInt(0, 3),
            }
        }));
    }

    // 6. Vehículos
    console.log('🚛 [SEED] Creando 30 vehículos...');
    const vehiculos = [];
    const marcas = ['Volvo', 'Scania', 'Mercedes-Benz', 'MAN', 'DAF', 'Iveco', 'Freightliner'];

    for (let i = 1; i <= 30; i++) {
        vehiculos.push(await prisma.vehiculo.create({
            data: {
                placa: `ABC${String(i).padStart(3, '0')}`,
                tipo_vehiculo_id: random(tiposVehiculo).id,
                marca: random(marcas),
                modelo: `Modelo ${randomInt(2015, 2024)}`,
                anio: randomInt(2015, 2024),
                kilometraje_actual: randomFloat(50000, 500000),
            }
        }));
    }

    // 7. Neumáticos
    console.log('🛞 [SEED] Creando 100 neumáticos...');
    const neumaticos = [];
    const estados: any[] = [
        ...Array(60).fill('EN_STOCK'),          // 60% en stock
        ...Array(30).fill('INSTALADO'),         // 30% instalados
        ...Array(5).fill('EN_REPARACION'),      // 5% en reparación
        ...Array(5).fill('EN_REENCAUCHE'),      // 5% en reencauche
    ];

    for (let i = 1; i <= 100; i++) {
        const modelo = random(modelos);
        const estado = estados[i - 1];
        const profundidadInicial = modelo.profundidad_inicial_mm;
        const profundidadActual = estado === 'EN_STOCK' || estado === 'INSTALADO'
            ? randomFloat(profundidadInicial * 0.5, profundidadInicial * 0.9)
            : randomFloat(5, profundidadInicial * 0.7);

        const neumaticoData: any = {
            numero_serie: `NS${String(i).padStart(6, '0')}`,
            modelo_id: modelo.id,
            dot: `${randomInt(1, 52)}${randomInt(20, 24)}`,
            estado_actual: estado,
            profundidad_inicial_mm: profundidadInicial,
            profundidad_actual_mm: profundidadActual,
            presion_actual_psi: randomFloat(90, 120),
            kilometraje_acumulado: estado === 'EN_STOCK' ? 0 : randomInt(10000, 100000),
            reencauches_realizados: estado === 'EN_REENCAUCHE' ? randomInt(1, 2) : 0,
        };

        // Asignar ubicación según estado
        if (estado === 'EN_STOCK' || estado === 'EN_REPARACION' || estado === 'EN_REENCAUCHE') {
            neumaticoData.ubicacion_almacen_id = random(almacenes).id;
        } else if (estado === 'INSTALADO') {
            neumaticoData.ubicacion_vehiculo_id = random(vehiculos).id;
            // ubicacion_posicion_id lo dejaremos null por ahora (se asignará en montaje)
        }
        neumaticos.push(await prisma.neumatico.create({ data: neumaticoData }));
    }

    console.log('\n✅ [SEED] Seed completado exitosamente!\n');
    console.log('📊 Resumen:');
    console.log(`  - Fabricantes: ${fabricantes.length}`);
    console.log(`  - Tipos de Vehículo: ${tiposVehiculo.length}`);
    console.log(`  - Almacenes: ${almacenes.length}`);
    console.log(`  - Proveedores: ${proveedores.length}`);
    console.log(`  - Modelos de Neumáticos: ${modelos.length}`);
    console.log(`  - Vehículos: ${vehiculos.length}`);
    console.log(`  - Neumáticos: ${neumaticos.length}`);
    console.log(`\n  Total registros: ${fabricantes.length + tiposVehiculo.length + almacenes.length + proveedores.length + modelos.length + vehiculos.length + neumaticos.length}`);

    // Estadísticas de neumáticos por estado
    const estadisticas = neumaticos.reduce((acc, n) => {
        acc[n.estado_actual] = (acc[n.estado_actual] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    console.log('\n📈 Neumáticos por estado:');
    Object.entries(estadisticas).forEach(([estado, count]) => {
        console.log(`  - ${estado}: ${count}`);
    });
}

main()
    .catch((e) => {
        console.error('\n❌ [SEED] Error:', e.message);
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
