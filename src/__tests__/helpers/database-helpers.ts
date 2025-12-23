/**
 * Database test helpers
 * Provides utilities for managing test data
 */
import { prisma } from '@/lib/prisma';

/**
 * Clean all test data from database
 * Note: In test environment, we can safely delete test data
 * In real environment, be more selective
 */
export async function cleanTestData() {
    // Get test neumatico IDs first
    const testNeumaticos = await prisma.neumatico.findMany({
        where: { numero_serie: { startsWith: 'TEST-' } },
        select: { id: true }
    });
    const testNeumaticoIds = testNeumaticos.map(n => n.id);

    // Delete historial_estado_neumatico (FK to neumatico)
    if (testNeumaticoIds.length > 0) {
        await prisma.historialEstadoNeumatico.deleteMany({
            where: { neumatico_id: { in: testNeumaticoIds } }
        });

        // Delete eventos_neumaticos (FK to neumatico)
        await prisma.eventoNeumatico.deleteMany({
            where: { neumatico_id: { in: testNeumaticoIds } }
        });
    }

    // Now delete test neumaticos
    await prisma.neumatico.deleteMany({
        where: { numero_serie: { startsWith: 'TEST-' } }
    });

    // Delete test vehiculos
    await prisma.vehiculo.deleteMany({
        where: { placa: { startsWith: 'TEST-' } }
    });

    // Delete test almacenes
    await prisma.almacen.deleteMany({
        where: { nombre: { startsWith: '[TEST]' } }
    });

    // Delete test proveedores
    await prisma.proveedor.deleteMany({
        where: { nombre: { startsWith: '[TEST]' } }
    });

    // Delete test models
    await prisma.modeloNeumatico.deleteMany({
        where: { nombre: { endsWith: 'Test' } }
    });

    // Delete test manufacturers
    await prisma.fabricanteNeumatico.deleteMany({
        where: { nombre: { endsWith: 'Test' } }
    });
}

/**
 * Create test neumatico
 */
export async function createTestNeumatico(overrides: any = {}) {
    // First, ensure we have a modelo
    const modelo = await prisma.modeloNeumatico.findFirst();

    if (!modelo) {
        throw new Error('No modelo found in database. Please seed base data first.');
    }

    const neumatico = await prisma.neumatico.create({
        data: {
            numero_serie: `TEST-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            modelo_id: modelo.id,
            dot: '2024',
            estado_actual: 'EN_STOCK',
            profundidad_inicial_mm: 20,
            profundidad_actual_mm: 20,
            activo: true,
            ...overrides
        }
    });

    return neumatico;
}

/**
 * Create test vehiculo
 */
export async function createTestVehiculo(overrides: any = {}) {
    // Get a tipo_vehiculo
    const tipoVehiculo = await prisma.tipoVehiculo.findFirst();

    if (!tipoVehiculo) {
        throw new Error('No tipo_vehiculo found. Please seed base data first.');
    }

    const vehiculo = await prisma.vehiculo.create({
        data: {
            placa: `TEST-${Date.now()}`,
            tipo_vehiculo_id: tipoVehiculo.id,
            marca: 'Test Brand',
            modelo: 'Test Model',
            anio: 2024,
            activo: true,
            ...overrides
        }
    });

    return vehiculo;
}

/**
 * Create test almacen
 */
export async function createTestAlmacen(overrides: any = {}) {
    const almacen = await prisma.almacen.create({
        data: {
            nombre: `[TEST] Almacén Test ${Date.now()}`,
            tipo: 'PRINCIPAL',
            ...overrides
        }
    });

    return almacen;
}

/**
 * Create test proveedor
 */
export async function createTestProveedor(overrides: any = {}) {
    const proveedor = await prisma.proveedor.create({
        data: {
            tipo: 'FABRICANTE',
            nombre: `[TEST] Proveedor Test ${Date.now()}`,
            ruc: `TEST${Date.now()}`.substring(0, 20),
            ...overrides
        }
    });

    return proveedor;
}

/**
 * Setup test database
 * Call before each test suite
 */
export async function setupTestDatabase() {
    await cleanTestData();
}

/**
 * Teardown test database
 * Call after each test suite
 */
export async function teardownTestDatabase() {
    await cleanTestData();
    await prisma.$disconnect();
}
