/**
 * Integration Tests for GET /api/v1/reportes/certificados
 * Validates paginated list retrieval, search by folio/plate,
 * state filtering, and strict multi-tenant isolation.
 */

import { NextRequest } from 'next/server';
import { GET } from '@/app/api/v1/reportes/certificados/route';
import { prisma } from '@/lib/prisma';
import { auth } from '@/lib/auth/auth';
import { mockSessions } from '../helpers/auth-helpers';
import {
    setupTestDatabase,
    teardownTestDatabase,
    cleanTestData,
    createTestTipoVehiculo,
    createTestVehiculo,
} from '../helpers/database-helpers';
import { EstadoOperatividadEnum } from '@prisma/client';

jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn(),
}));

const BASE_URL = 'http://localhost:3000/api/v1/reportes/certificados';

describe('GET /api/v1/reportes/certificados Integration Tests', () => {
    let empresaA: any;
    let empresaB: any;
    let vehiculoA: any;
    let vehiculoB: any;
    let certA1: any;
    let certA2: any;
    let certB1: any;

    beforeAll(async () => {
        await setupTestDatabase();

        const ts = Date.now().toString().slice(-8);
        empresaA = await prisma.empresa.create({
            data: { nombre: 'Empresa Certs A ' + ts, ruc: '20' + ts + '81' },
        });

        empresaB = await prisma.empresa.create({
            data: { nombre: 'Empresa Certs B ' + ts, ruc: '20' + ts + '82' },
        });

        const tipoVehiculo = await prisma.tipoVehiculo.create({
            data: { nombre: 'Camión Test ' + ts },
        });

        const ts4 = ts.slice(-4);
        vehiculoA = await prisma.vehiculo.create({
            data: {
                placa: 'T-A1-' + ts4,
                numero_economico: 'EA1-' + ts4,
                empresa_id: empresaA.id,
                tipo_vehiculo_id: tipoVehiculo.id,
            },
        });

        vehiculoB = await prisma.vehiculo.create({
            data: {
                placa: 'T-B1-' + ts4,
                numero_economico: 'EB1-' + ts4,
                empresa_id: empresaB.id,
                tipo_vehiculo_id: tipoVehiculo.id,
            },
        });

        const user = await prisma.usuario.create({
            data: {
                username: 'testuser_cert_' + ts,
                email: 'testuser_cert_' + ts + '@example.com',
                password_hash: 'hash',
                nombre_completo: 'Inspector Test ' + ts,
                empresa_id: empresaA.id,
            },
        });

        // Crear certificados para Empresa A
        certA1 = await prisma.certificadoEmitido.create({
            data: {
                empresa_id: empresaA.id,
                vehiculo_id: vehiculoA.id,
                emitido_por: user.id,
                folio_numero: 1001,
                estado_operatividad: EstadoOperatividadEnum.APTO,
                snapshot_data: { vehiculo: { placa: vehiculoA.placa } },
            },
        });

        certA2 = await prisma.certificadoEmitido.create({
            data: {
                empresa_id: empresaA.id,
                vehiculo_id: vehiculoA.id,
                emitido_por: user.id,
                folio_numero: 1002,
                estado_operatividad: EstadoOperatividadEnum.NO_APTO,
                snapshot_data: { vehiculo: { placa: vehiculoA.placa } },
            },
        });

        // Crear certificado para Empresa B
        certB1 = await prisma.certificadoEmitido.create({
            data: {
                empresa_id: empresaB.id,
                vehiculo_id: vehiculoB.id,
                emitido_por: user.id,
                folio_numero: 1001,
                estado_operatividad: EstadoOperatividadEnum.CONDICIONAL,
                snapshot_data: { vehiculo: { placa: vehiculoB.placa } },
            },
        });
    });

    afterAll(async () => {
        await cleanTestData();
        await teardownTestDatabase();
    });

    it('debe retornar 401 si no está autenticado', async () => {
        (auth as jest.Mock).mockResolvedValue(null);

        const req = new NextRequest(BASE_URL);
        const res = await GET(req, { params: Promise.resolve({}) });

        expect(res.status).toBe(401);
    });

    it('debe listar solo los certificados pertenecientes al tenant autenticado (Multi-tenant isolation)', async () => {
        const sessionA = {
            ...mockSessions.admin,
            user: { ...mockSessions.admin.user, empresa_id: empresaA.id },
        };
        (auth as jest.Mock).mockResolvedValue(sessionA);

        const req = new NextRequest(BASE_URL);
        const res = await GET(req, { params: Promise.resolve({}) });

        expect(res.status).toBe(200);
        const body = await res.json();

        expect(body.success).toBeTruthy();
        expect(body.data.length).toBe(2); // certA1 y certA2
        expect(body.pagination.total).toBe(2);

        const folios = body.data.map((c: any) => c.folio_numero);
        expect(folios).toContain(1001);
        expect(folios).toContain(1002);
    });

    it('debe filtrar por búsqueda de folio numérico y por placa', async () => {
        const sessionA = {
            ...mockSessions.admin,
            user: { ...mockSessions.admin.user, empresa_id: empresaA.id },
        };
        (auth as jest.Mock).mockResolvedValue(sessionA);

        // Búsqueda por folio
        const reqFolio = new NextRequest(`${BASE_URL}?q=1002`);
        const resFolio = await GET(reqFolio, { params: Promise.resolve({}) });
        const bodyFolio = await resFolio.json();

        expect(bodyFolio.data.length).toBe(1);
        expect(bodyFolio.data[0].folio_numero).toBe(1002);

        // Búsqueda por placa
        const reqPlaca = new NextRequest(`${BASE_URL}?q=${vehiculoA.placa}`);
        const resPlaca = await GET(reqPlaca, { params: Promise.resolve({}) });
        const bodyPlaca = await resPlaca.json();

        expect(bodyPlaca.data.length).toBe(2);
    });

    it('debe filtrar por estado de operatividad', async () => {
        const sessionA = {
            ...mockSessions.admin,
            user: { ...mockSessions.admin.user, empresa_id: empresaA.id },
        };
        (auth as jest.Mock).mockResolvedValue(sessionA);

        const req = new NextRequest(`${BASE_URL}?estado=NO_APTO`);
        const res = await GET(req, { params: Promise.resolve({}) });
        const body = await res.json();

        expect(body.data.length).toBe(1);
        expect(body.data[0].estado_operatividad).toBe('NO_APTO');
    });
});
