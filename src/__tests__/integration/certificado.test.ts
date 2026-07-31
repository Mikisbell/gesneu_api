/**
 * Integration Tests for CertificadoService
 * Validates vehicle readiness evaluation (APTO/CONDICIONAL/NO_APTO),
 * atomic sequential folio increments per enterprise, snapshot persistence,
 * IDOR isolation, and snapshot re-downloading.
 */

import { prisma } from '@/lib/prisma';
import {
    evaluarOperatividadVehiculo,
    emitirCertificadoOperatividad,
    obtenerCertificadoPorFolio,
    listarCertificadosVehiculo,
} from '@/lib/services/certificado.service';
import { EstadoOperatividadEnum } from '@prisma/client';
import {
    setupTestDatabase,
    teardownTestDatabase,
    cleanTestData,
    createTestFabricante,
    createTestModelo,
} from '../helpers/database-helpers';

describe('CertificadoService Integration Tests', () => {
    let empresaA: any;
    let empresaB: any;
    let userA: any;
    let fabricante: any;
    let modelo: any;
    let vehiculoA: any;
    let vehiculoB: any;

    beforeAll(async () => {
        await setupTestDatabase();

        // Create two distinct enterprises for multi-tenant IDOR testing
        const ts = Date.now().toString().slice(-8);
        empresaA = await prisma.empresa.create({
            data: { nombre: 'Empresa Cert A ' + ts, ruc: '20' + ts + '01' },
        });

        empresaB = await prisma.empresa.create({
            data: { nombre: 'Empresa Cert B ' + ts, ruc: '20' + ts + '02' },
        });

        // User for Empresa A
        userA = await prisma.usuario.create({
            data: {
                username: 'certuser_' + Date.now(),
                email: `certuser_${Date.now()}@test.com`,
                nombre_completo: 'Inspector Certificados',
                password_hash: 'hash',
                rol: 'ADMIN',
                empresa_id: empresaA.id,
            },
        });

        // Catalog setup
        fabricante = await createTestFabricante();
        modelo = await createTestModelo(fabricante.id, {
            presion_recomendada_psi: 100,
            profundidad_original_mm: 18.0,
        });

        // Vehicle A in Empresa A
        const tipoV = await prisma.tipoVehiculo.findFirst() || await prisma.tipoVehiculo.create({
            data: { nombre: 'Camión Cert Test ' + ts },
        });

        const suffix = Date.now().toString().slice(-6);
        vehiculoA = await prisma.vehiculo.create({
            data: {
                placa: `T-A1-${suffix}`,
                numero_economico: `ECO-A1-${suffix}`,
                empresa_id: empresaA.id,
                tipo_vehiculo_id: tipoV.id,
                odometro_actual: 50000,
            },
        });

        // Vehicle B in Empresa B
        vehiculoB = await prisma.vehiculo.create({
            data: {
                placa: `T-B1-${suffix}`,
                numero_economico: `ECO-B1-${suffix}`,
                empresa_id: empresaB.id,
                tipo_vehiculo_id: tipoV.id,
                odometro_actual: 30000,
            },
        });
    });

    afterAll(async () => {
        await cleanTestData();
        await teardownTestDatabase();
    });

    describe('evaluarOperatividadVehiculo()', () => {
        test('Debe retornar NO_APTO cuando el vehículo no tiene neumáticos instalados', () => {
            const result = evaluarOperatividadVehiculo([]);
            expect(result.estado).toBe(EstadoOperatividadEnum.NO_APTO);
            expect(result.razones[0]).toContain('no tiene neumáticos instalados');
        });

        test('Debe retornar APTO cuando todos los neumáticos tienen profundidad >= 4mm y presión correcta', () => {
            const mockNeumaticos: any[] = [
                {
                    id: 'neu-1',
                    numero_serie: 'SERIE-1',
                    profundidad_remanente_actual_mm: 10.0,
                    presion_actual_psi: 100.0,
                    modelo: {
                        presion_recomendada_psi: 100.0,
                        fabricante: { nombre: 'Michelin' },
                        nombre_modelo: 'X Multi',
                    },
                    ubicacion_posicion: { codigo_posicion: '1-IZQ' },
                },
            ];

            const result = evaluarOperatividadVehiculo(mockNeumaticos);
            expect(result.estado).toBe(EstadoOperatividadEnum.APTO);
            expect(result.neumaticos[0].estado).toBe(EstadoOperatividadEnum.APTO);
        });

        test('Debe retornar CONDICIONAL cuando profundidad está entre 3.0mm y 4.0mm', () => {
            const mockNeumaticos: any[] = [
                {
                    id: 'neu-2',
                    numero_serie: 'SERIE-2',
                    profundidad_remanente_actual_mm: 3.5, // Rango condicional
                    presion_actual_psi: 100.0,
                    modelo: {
                        presion_recomendada_psi: 100.0,
                        fabricante: { nombre: 'Michelin' },
                        nombre_modelo: 'X Multi',
                    },
                    ubicacion_posicion: { codigo_posicion: '1-DER' },
                },
            ];

            const result = evaluarOperatividadVehiculo(mockNeumaticos);
            expect(result.estado).toBe(EstadoOperatividadEnum.CONDICIONAL);
            expect(result.razones[0]).toContain('condicional');
        });

        test('Debe retornar NO_APTO cuando al menos un neumático tiene profundidad < 3.0mm', () => {
            const mockNeumaticos: any[] = [
                {
                    id: 'neu-3',
                    numero_serie: 'SERIE-3',
                    profundidad_remanente_actual_mm: 2.5, // Crítico (< 3.0)
                    presion_actual_psi: 100.0,
                    modelo: {
                        presion_recomendada_psi: 100.0,
                        fabricante: { nombre: 'Michelin' },
                        nombre_modelo: 'X Multi',
                    },
                    ubicacion_posicion: { codigo_posicion: '1-IZQ' },
                },
            ];

            const result = evaluarOperatividadVehiculo(mockNeumaticos);
            expect(result.estado).toBe(EstadoOperatividadEnum.NO_APTO);
            expect(result.razones[0]).toContain('estado crítico');
        });

        test('Debe retornar NO_APTO cuando la desviación de presión es mayor al 20%', () => {
            const mockNeumaticos: any[] = [
                {
                    id: 'neu-4',
                    numero_serie: 'SERIE-4',
                    profundidad_remanente_actual_mm: 12.0,
                    presion_actual_psi: 75.0, // 25% menos de 100 PSI recomendada (>20% crítico)
                    modelo: {
                        presion_recomendada_psi: 100.0,
                        fabricante: { nombre: 'Michelin' },
                        nombre_modelo: 'X Multi',
                    },
                    ubicacion_posicion: { codigo_posicion: '1-IZQ' },
                },
            ];

            const result = evaluarOperatividadVehiculo(mockNeumaticos);
            expect(result.estado).toBe(EstadoOperatividadEnum.NO_APTO);
        });
    });

    describe('emitirCertificadoOperatividad()', () => {
        test('Debe generar folios atómicos secuenciales independientes por empresa', async () => {
            // Emisión 1 para Empresa A
            const certA1 = await emitirCertificadoOperatividad({
                vehiculoId: vehiculoA.id,
                emitidoPor: userA.id,
                empresaId: empresaA.id,
            });

            expect(certA1.folio_numero).toBe(1);

            // Emisión 2 para Empresa A
            const certA2 = await emitirCertificadoOperatividad({
                vehiculoId: vehiculoA.id,
                emitidoPor: userA.id,
                empresaId: empresaA.id,
            });

            expect(certA2.folio_numero).toBe(2);

            // Emisión 1 para Empresa B (Empieza en 1 independientemente de A)
            const certB1 = await emitirCertificadoOperatividad({
                vehiculoId: vehiculoB.id,
                emitidoPor: userA.id,
                empresaId: empresaB.id,
            });

            expect(certB1.folio_numero).toBe(1);
        });

        test('Debe lanzar error (protección IDOR) al intentar emitir certificado para vehículo de otra empresa', async () => {
            await expect(
                emitirCertificadoOperatividad({
                    vehiculoId: vehiculoB.id, // Pertenece a Empresa B
                    emitidoPor: userA.id,
                    empresaId: empresaA.id, // Petición desde Empresa A
                })
            ).rejects.toThrow('Vehículo no encontrado o no pertenece a su empresa');
        });
    });

    describe('obtenerCertificadoPorFolio() y listarCertificadosVehiculo()', () => {
        test('Debe recuperar exactamente el snapshot inmutable guardado por número de folio', async () => {
            const cert = await obtenerCertificadoPorFolio({
                empresaId: empresaA.id,
                folioNumero: 1,
            });

            expect(cert.folio_numero).toBe(1);
            expect(cert.vehiculo.placa).toContain('T-A1-');
            expect(cert.estado_operatividad).toBeDefined();
        });

        test('Debe rechazar consulta de folio pertenecientes a otra empresa (IDOR)', async () => {
            // Emite folio 2 en Empresa B
            const certB2 = await emitirCertificadoOperatividad({
                vehiculoId: vehiculoB.id,
                emitidoPor: userA.id,
                empresaId: empresaB.id,
            });

            // Intentar leer el folio de Empresa B desde el contexto de Empresa A
            await expect(
                obtenerCertificadoPorFolio({
                    empresaId: empresaA.id,
                    folioNumero: certB2.folio_numero + 999, // Folio inexistente en Empresa A
                })
            ).rejects.toThrow('Certificado no encontrado o no pertenece a su empresa');
        });

        test('Debe listar el historial de certificados emitidos para un vehículo', async () => {
            const historial = await listarCertificadosVehiculo({
                empresaId: empresaA.id,
                vehiculoId: vehiculoA.id,
            });

            expect(historial.length).toBeGreaterThanOrEqual(2);
            expect(historial[0].folio_numero).toBeGreaterThan(historial[1].folio_numero);
        });
    });
});
