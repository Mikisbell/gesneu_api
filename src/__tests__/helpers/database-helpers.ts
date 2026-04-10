
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
export async function getOrCreateTestEnterprise() {
    // RLS might block reading, so we create a new one every time
    // This is safer for tests anyway to ensure isolation
    const empresa = await prisma.empresa.create({
        data: {
            nombre: `Test Enterprise ${Date.now()}`,
            ruc: `TEST${Date.now()}`.substring(0, 20),
        }
    });
    return empresa;
}

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

        // Delete alertas (FK to neumatico)
        await prisma.alerta.deleteMany({
            where: { neumatico_id: { in: testNeumaticoIds } }
        });

        // ✅ FIX: Delete lecturas_presion (FK to neumatico)
        await prisma.lecturaPresion.deleteMany({
            where: { neumatico_id: { in: testNeumaticoIds } }
        });

        // ✅ FIX: Delete inspecciones (FK to neumatico)
        await prisma.inspeccion.deleteMany({
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
        where: { nombre_modelo: { endsWith: 'Test' } }
    });

    // Delete test manufacturers
    await prisma.fabricanteNeumatico.deleteMany({
        where: { nombre: { endsWith: 'Test' } }
    });

    // Delete test users (generic cleanup for created users)
    await prisma.usuario.deleteMany({
        where: { username: { startsWith: 'testuser_' } }
    });
}

/**
 * Create test fabricante
 */
export async function createTestFabricante(empresaId?: string) {
    return await prisma.fabricanteNeumatico.create({
        data: {
            nombre: `Michelin Test ${Date.now()}`,
        }
    });
}

/**
 * Create test modelo
 */
export async function createTestModelo(fabricanteId: string, overrides: any = {}) {
    return await prisma.modeloNeumatico.create({
        data: {
            nombre_modelo: `X Multi Z Test ${Date.now()}`,
            medida: '295/80R22.5',
            profundidad_original_mm: 18.5,
            fabricante_id: fabricanteId,
            reencauches_maximos: 2,
            ...overrides
        }
    });
}

/**
 * Create test neumatico
 * Updated signature to accept modeloId and empresaId explicitly
 */
export async function createTestNeumatico(modeloIdOrOverrides?: string | any, empresaIdOrOverrides?: string | any) {
    let modelo_id: string;
    let empresa_id: string;
    let overrides: any = {};

    // Handle different parameter combinations
    if (typeof modeloIdOrOverrides === 'string') {
        // First param is modeloId
        modelo_id = modeloIdOrOverrides;
        if (typeof empresaIdOrOverrides === 'string') {
            empresa_id = empresaIdOrOverrides;
        } else {
            empresa_id = (await getOrCreateTestEnterprise()).id;
            overrides = empresaIdOrOverrides || {};
        }
    } else {
        // Legacy mode: first param is overrides object
        overrides = modeloIdOrOverrides || {};
        // Ensure modelo exists
        let modelo = await prisma.modeloNeumatico.findFirst({
            where: { nombre_modelo: { endsWith: 'Test' } }
        });

        if (!modelo) {
            const fabricante = await createTestFabricante();
            modelo = await createTestModelo(fabricante.id);
        }
        modelo_id = modelo.id;
        empresa_id = (await getOrCreateTestEnterprise()).id;
    }

    return await prisma.neumatico.create({
        data: {
            numero_serie: `TEST-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
            modelo_id,
            empresa_id,
            fecha_compra: new Date(),
            profundidad_inicial_mm: 18,
            profundidad_remanente_actual_mm: 18,
            estado_actual: 'EN_STOCK',
            costo_compra: 0,
            kilometraje_acumulado: 0,
            activo: true,
            ...overrides
        }
    });
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
            placa: `T${Date.now().toString().slice(-8)}`,
            numero_economico: `E${Date.now().toString().slice(-8)}`,
            tipo_vehiculo_id: tipoVehiculo.id,
            marca: 'Test Brand',
            modelo_vehiculo: 'Test Model',
            anio_fabricacion: 2024,
            empresa_id: (await getOrCreateTestEnterprise()).id,
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
            empresa_id: (await getOrCreateTestEnterprise()).id,
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
            empresa_id: (await getOrCreateTestEnterprise()).id,
            ...overrides
        }
    });

    return proveedor;
}

/**
 * Create test user
 */
export async function createTestUser(overrides: any = {}) {
    return await prisma.usuario.create({
        data: {
            username: 'testuser_' + Date.now() + Math.random().toString(36).substr(2, 5),
            email: 'test_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5) + '@example.com',
            password_hash: 'hashed_password',
            nombre_completo: 'Test User',
            rol: 'ADMIN',
            empresa_id: (await getOrCreateTestEnterprise()).id,
            ...overrides
        }
    });
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
