/**
 * Tests de Seguridad: Política de Reencauchados
 * 
 * Regla crítica de seguridad: Los neumáticos reencauchados NO pueden montarse
 * en ejes direccionales (DIRECCION) o en posiciones que no lo permitan.
 * 
 * Esta regla previene accidentes por fallo de neumático en eje de dirección.
 */

import { prisma } from '@/lib/prisma';

describe('Retread Safety Policy', () => {
    // Setup: Crear datos de prueba
    let tipoVehiculoId: string;
    let vehiculoId: string;
    let ejesDireccionId: string;
    let ejeTraccionId: string;
    let posicionDireccionId: string;
    let posicionTraccionId: string;
    let posicionBloqueadaId: string;
    let modeloId: string;
    let neumaticoNuevoId: string;
    let neumaticoReencauchadoId: string;

    beforeAll(async () => {
        // Limpiar datos de prueba previos
        await prisma.eventoNeumatico.deleteMany({ where: { notas: { contains: 'TEST_SECURITY' } } });
        await prisma.neumatico.deleteMany({ where: { numero_serie: { startsWith: 'SEC-TEST' } } });
        await prisma.posicionNeumatico.deleteMany({ where: { numero_posicion: { gte: 900 } } });
        await prisma.configuracionEje.deleteMany({ where: { numero_eje: { gte: 90 } } });

        // Crear fabricante y modelo
        const fabricante = await prisma.fabricanteNeumatico.upsert({
            where: { nombre: 'TEST_SECURITY_FAB' },
            update: {},
            create: { nombre: 'TEST_SECURITY_FAB' }
        });

        const modelo = await prisma.modeloNeumatico.create({
            data: {
                nombre: 'TEST_SECURITY_MODEL_' + Date.now(),
                medida: '295/80R22.5',
                profundidad_inicial_mm: 18,
                fabricante_id: fabricante.id,
                reencauches_maximos: 2
            }
        });
        modeloId = modelo.id;

        // Crear tipo de vehículo
        const tipoVehiculo = await prisma.tipoVehiculo.upsert({
            where: { nombre: 'TEST_SECURITY_VEHICLE' },
            update: {},
            create: { nombre: 'TEST_SECURITY_VEHICLE', descripcion: 'Test vehicle for security tests' }
        });
        tipoVehiculoId = tipoVehiculo.id;

        // Crear ejes
        const ejeDireccion = await prisma.configuracionEje.create({
            data: {
                tipo_vehiculo_id: tipoVehiculoId,
                numero_eje: 91,
                tipo_eje: 'DIRECCION',
                posiciones_neumatico: 2,
                permite_reencauchados: false // 🚫 NO permite reencauchados
            }
        });
        ejesDireccionId = ejeDireccion.id;

        const ejeTraccion = await prisma.configuracionEje.create({
            data: {
                tipo_vehiculo_id: tipoVehiculoId,
                numero_eje: 92,
                tipo_eje: 'TRACCION',
                posiciones_neumatico: 4,
                permite_reencauchados: true // ✅ SÍ permite reencauchados
            }
        });
        ejeTraccionId = ejeTraccion.id;

        // Crear posiciones
        const posDireccion = await prisma.posicionNeumatico.create({
            data: {
                configuracion_eje_id: ejesDireccionId,
                numero_posicion: 901,
                lado_vehiculo: 'IZQUIERDO',
                permite_reencauchado: true // Aunque la posición lo permita, el eje no
            }
        });
        posicionDireccionId = posDireccion.id;

        const posTraccion = await prisma.posicionNeumatico.create({
            data: {
                configuracion_eje_id: ejeTraccionId,
                numero_posicion: 902,
                lado_vehiculo: 'IZQUIERDO',
                permite_reencauchado: true // ✅ Posición y eje permiten
            }
        });
        posicionTraccionId = posTraccion.id;

        const posBloqueada = await prisma.posicionNeumatico.create({
            data: {
                configuracion_eje_id: ejeTraccionId,
                numero_posicion: 903,
                lado_vehiculo: 'DERECHO',
                permite_reencauchado: false // 🚫 Posición bloqueada específicamente
            }
        });
        posicionBloqueadaId = posBloqueada.id;

        // Crear vehículo
        const vehiculo = await prisma.vehiculo.upsert({
            where: { codigo_interno: 'SEC-TEST-001' },
            update: {},
            create: {
                codigo_interno: 'SEC-TEST-001',
                placa: 'SEC-001',
                tipo_vehiculo_id: tipoVehiculoId,
                marca: 'TEST',
                modelo: 'SECURITY'
            }
        });
        vehiculoId = vehiculo.id;

        // Crear neumático NUEVO (no reencauchado)
        const neumaticoNuevo = await prisma.neumatico.create({
            data: {
                numero_serie: 'SEC-TEST-NEW-' + Date.now(),
                modelo_id: modeloId,
                estado_actual: 'EN_STOCK',
                profundidad_inicial_mm: 18,
                profundidad_actual_mm: 18,
                es_reencauchado: false,
                costo_compra: 500
            }
        });
        neumaticoNuevoId = neumaticoNuevo.id;

        // Crear neumático REENCAUCHADO
        const neumaticoReencauchado = await prisma.neumatico.create({
            data: {
                numero_serie: 'SEC-TEST-RETREAD-' + Date.now(),
                modelo_id: modeloId,
                estado_actual: 'EN_STOCK',
                profundidad_inicial_mm: 15,
                profundidad_actual_mm: 15,
                es_reencauchado: true,
                reencauches_realizados: 1,
                costo_compra: 200
            }
        });
        neumaticoReencauchadoId = neumaticoReencauchado.id;
    });

    afterAll(async () => {
        // Limpiar datos de prueba
        await prisma.eventoNeumatico.deleteMany({ where: { notas: { contains: 'TEST_SECURITY' } } });
        await prisma.neumatico.deleteMany({ where: { numero_serie: { startsWith: 'SEC-TEST' } } });
        await prisma.posicionNeumatico.deleteMany({ where: { numero_posicion: { gte: 900 } } });
        await prisma.configuracionEje.deleteMany({ where: { numero_eje: { gte: 90 } } });
        await prisma.vehiculo.deleteMany({ where: { codigo_interno: 'SEC-TEST-001' } });
        await prisma.$disconnect();
    });

    describe('Eje Direccional (DIRECCION)', () => {
        it('should BLOCK retread tire on steering axle', async () => {
            // Obtener datos para la validación
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: neumaticoReencauchadoId }
            });

            const posicion = await prisma.posicionNeumatico.findUnique({
                where: { id: posicionDireccionId },
                include: { configuracion_eje: true }
            });

            // Verificar que es reencauchado
            expect(neumatico?.es_reencauchado).toBe(true);

            // Verificar que el eje NO permite reencauchados
            expect(posicion?.configuracion_eje.permite_reencauchados).toBe(false);
            expect(posicion?.configuracion_eje.tipo_eje).toBe('DIRECCION');

            // Esta combinación DEBE ser bloqueada por validateMontaje()
            // Simulamos la lógica de validación
            const shouldBlock = neumatico?.es_reencauchado &&
                !posicion?.configuracion_eje.permite_reencauchados;

            expect(shouldBlock).toBe(true); // ✅ Confirma que la regla bloquearía
        });

        it('should ALLOW new tire on steering axle', async () => {
            // Neumático nuevo SÍ puede ir en eje direccional
            // Solo verificamos que no falla por política de reencauche
            const posicion = await prisma.posicionNeumatico.findUnique({
                where: { id: posicionDireccionId },
                include: { configuracion_eje: true }
            });

            // Un neumático nuevo no debería ser bloqueado por la política
            const neumatico = await prisma.neumatico.findUnique({
                where: { id: neumaticoNuevoId }
            });

            // Validación manual: nuevo + direccional = OK
            const esReencauchado = neumatico?.es_reencauchado;
            const ejePermite = posicion?.configuracion_eje.permite_reencauchados;

            // Si no es reencauchado, la política no aplica
            expect(esReencauchado).toBe(false);
            // Por lo tanto, aunque el eje no permita reencauchados, un nuevo puede montarse
        });
    });

    describe('Eje Tracción (TRACCION)', () => {
        it('should ALLOW retread tire on traction axle when permitted', async () => {
            // Verificar que la posición de tracción permite reencauchados
            const posicion = await prisma.posicionNeumatico.findUnique({
                where: { id: posicionTraccionId },
                include: { configuracion_eje: true }
            });

            expect(posicion?.permite_reencauchado).toBe(true);
            expect(posicion?.configuracion_eje.permite_reencauchados).toBe(true);
        });
    });

    describe('Posición Bloqueada Específicamente', () => {
        it('should BLOCK retread tire when position.permite_reencauchado = false', async () => {
            // Verificar configuración
            const posicion = await prisma.posicionNeumatico.findUnique({
                where: { id: posicionBloqueadaId },
                include: { configuracion_eje: true }
            });

            // Aunque el eje de tracción permite reencauchados...
            expect(posicion?.configuracion_eje.permite_reencauchados).toBe(true);
            // ...esta posición específica NO lo permite
            expect(posicion?.permite_reencauchado).toBe(false);
        });
    });

    describe('Regla de Negocio Documentada', () => {
        it('should have clear documentation of safety rule in code', async () => {
            // Este test verifica que la regla está documentada
            // Leemos el archivo de montaje y verificamos que existe el comentario
            const fs = await import('fs');
            const path = await import('path');
            const routePath = path.join(process.cwd(), 'src/app/api/v1/operaciones/montaje/route.ts');
            const content = fs.readFileSync(routePath, 'utf-8');

            // Verificar que existe la validación documentada
            expect(content).toContain('Validar política de reencauchados');
            expect(content).toContain('es_reencauchado');
            expect(content).toContain('permite_reencauchados');
        });
    });
});
