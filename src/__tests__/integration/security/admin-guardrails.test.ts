/**
 * Integration Tests for Security Guardrails
 * Verifies that dynamic RBAC and Multi-Tenant administration endpoints
 * strictly return HTTP 501 FEATURE_DISABLED in single-tenant mode.
 */

import { NextRequest } from 'next/server';
import { GET as GET_ROLES, POST as POST_ROLES } from '@/app/api/v1/admin/roles/route';
import { GET as GET_ROLE_BY_ID, PUT as PUT_ROLE, DELETE as DELETE_ROLE } from '@/app/api/v1/admin/roles/[id]/route';
import { POST as POST_ROLE_PERMISO, DELETE as DELETE_ROLE_PERMISO } from '@/app/api/v1/admin/roles/[id]/permisos/route';
import { POST as POST_USER_ROLE, DELETE as DELETE_USER_ROLE } from '@/app/api/v1/admin/users/[id]/roles/route';
import { GET as GET_TENANTS, POST as POST_TENANTS } from '@/app/api/v1/admin/tenants/route';
import { GET as GET_TENANT_BY_ID } from '@/app/api/v1/admin/tenants/[id]/route';
import { auth } from '@/lib/auth/auth';
import { mockSessions } from '../../helpers/auth-helpers';

// Mock auth module
jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn()
}));

const mockAuth = auth as unknown as jest.Mock;
const FAKE_UUID = '00000000-0000-0000-0000-000000000001';

describe('Admin Security Guardrails (FEATURE_DISABLED Verification)', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        // Set mock session to ADMIN to ensure requests pass auth layer before hitting feature flag guard
        mockAuth.mockResolvedValue(mockSessions.admin);
    });

    describe('Dynamic RBAC Guardrails (DYNAMIC_RBAC_ENABLED = false)', () => {
        test('GET /api/v1/admin/roles debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest('http://localhost:3000/api/v1/admin/roles');
            const res = await (GET_ROLES as any)(req, { params: Promise.resolve({}) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.success).toBeFalsy();
            expect(json.code).toBe('FEATURE_DISABLED');
            expect(json.error).toContain('RBAC dinámico');
        });

        test('POST /api/v1/admin/roles debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest('http://localhost:3000/api/v1/admin/roles', {
                method: 'POST',
                body: JSON.stringify({ nombre: 'Nuevo Rol Custom' })
            });
            const res = await (POST_ROLES as any)(req, { params: Promise.resolve({}) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('GET /api/v1/admin/roles/[id] debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/roles/${FAKE_UUID}`);
            const res = await GET_ROLE_BY_ID(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('PUT /api/v1/admin/roles/[id] debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/roles/${FAKE_UUID}`, {
                method: 'PUT',
                body: JSON.stringify({ nombre: 'Rol Editado' })
            });
            const res = await PUT_ROLE(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('DELETE /api/v1/admin/roles/[id] debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/roles/${FAKE_UUID}`, {
                method: 'DELETE'
            });
            const res = await DELETE_ROLE(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('POST /api/v1/admin/roles/[id]/permisos debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/roles/${FAKE_UUID}/permisos`, {
                method: 'POST',
                body: JSON.stringify({ permiso_id: FAKE_UUID })
            });
            const res = await POST_ROLE_PERMISO(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('DELETE /api/v1/admin/roles/[id]/permisos debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/roles/${FAKE_UUID}/permisos?permiso_id=${FAKE_UUID}`, {
                method: 'DELETE'
            });
            const res = await DELETE_ROLE_PERMISO(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('POST /api/v1/admin/users/[id]/roles debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/users/${FAKE_UUID}/roles`, {
                method: 'POST',
                body: JSON.stringify({ rol_id: FAKE_UUID })
            });
            const res = await POST_USER_ROLE(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('DELETE /api/v1/admin/users/[id]/roles debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/users/${FAKE_UUID}/roles?rol_id=${FAKE_UUID}`, {
                method: 'DELETE'
            });
            const res = await DELETE_USER_ROLE(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });
    });

    describe('Multi-Tenant Guardrails (MULTI_TENANT_ENABLED = false)', () => {
        test('GET /api/v1/admin/tenants debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest('http://localhost:3000/api/v1/admin/tenants');
            const res = await GET_TENANTS(req);

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.success).toBeFalsy();
            expect(json.code).toBe('FEATURE_DISABLED');
            expect(json.error).toContain('Gestión multi-tenant');
        });

        test('POST /api/v1/admin/tenants debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest('http://localhost:3000/api/v1/admin/tenants', {
                method: 'POST',
                body: JSON.stringify({ nombre: 'Empresa Test', ruc: '12345678901' })
            });
            const res = await POST_TENANTS(req);

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });

        test('GET /api/v1/admin/tenants/[id] debe retornar 501 FEATURE_DISABLED', async () => {
            const req = new NextRequest(`http://localhost:3000/api/v1/admin/tenants/${FAKE_UUID}`);
            const res = await GET_TENANT_BY_ID(req, { params: Promise.resolve({ id: FAKE_UUID }) });

            expect(res.status).toBe(501);
            const json = await res.json();
            expect(json.code).toBe('FEATURE_DISABLED');
        });
    });
});
