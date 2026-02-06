
import { createMocks } from 'node-mocks-http';
import { GET, POST } from '@/app/api/v1/webhooks/route';
import { prisma } from '@/lib/prisma';
import { createMockSession } from '../../helpers/auth-helpers';
import { getOrCreateTestEnterprise } from '../../helpers/database-helpers';

// Mock auth module
jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn(),
}));

// Mock requireAuth/requireRole to allow us to control the session returned
jest.mock('@/lib/auth/authorization', () => {
    const originalModule = jest.requireActual('@/lib/auth/authorization');
    return {
        ...originalModule,
        requireAuth: jest.fn(),
        // We use the real requireRole to test its logic, or we can mock it if we trust it.
        // Better: Mock auth() and let requireAuth use it.
        // But authorization.ts imports auth from ./auth. 
        // If we mock ./auth, requireAuth should pick it up if it uses the imported one.
    };
});

// Actually, simpler approach: Mock requireAuth directly to return our custom session
import { requireAuth } from '@/lib/auth/authorization';

describe('Webhook Security & Isolation', () => {
    let tenantA: any;
    let tenantB: any;
    let userA: any;
    let userB: any;

    beforeAll(async () => {
        // Create two distinct tenants
        tenantA = await prisma.empresa.create({
            data: { nombre: 'Tenant A ' + Date.now(), ruc: 'RUC-A-' + Date.now() }
        });
        tenantB = await prisma.empresa.create({
            data: { nombre: 'Tenant B ' + Date.now(), ruc: 'RUC-B-' + Date.now() }
        });

        // Create users for FK constraints
        userA = await prisma.usuario.create({
            data: {
                username: 'admin-a-' + Date.now(),
                email: 'admin-a-' + Date.now() + '@test.com',
                nombre_completo: 'Admin A',
                password_hash: 'hash',
                rol: 'OPERADOR', // Role string matches enum, though we set ADMIN in session mock
                empresa_id: tenantA.id
            }
        });

        userB = await prisma.usuario.create({
            data: {
                username: 'admin-b-' + Date.now(),
                email: 'admin-b-' + Date.now() + '@test.com',
                nombre_completo: 'Admin B',
                password_hash: 'hash',
                rol: 'OPERADOR',
                empresa_id: tenantB.id
            }
        });
    });

    afterAll(async () => {
        // Cleanup
        await prisma.webhookConfig.deleteMany({ where: { empresa_id: { in: [tenantA.id, tenantB.id] } } });
        await prisma.usuario.deleteMany({ where: { id: { in: [userA.id, userB.id] } } });
        await prisma.empresa.deleteMany({ where: { id: { in: [tenantA.id, tenantB.id] } } });
    });

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('RBAC Standardization', () => {
        it('should block user without ADMIN role', async () => {
            const session = createMockSession({
                roles: ['OPERADOR'],
                userId: 'user-op',
                username: 'op'
            });
            (requireAuth as jest.Mock).mockResolvedValue(session);

            const { req } = createMocks({ method: 'GET' });
            // @ts-ignore
            const res = await GET(req);

            // Should be 403 or Error thrown depending on implementation
            // Our implementation throws Error in requireRole, caught by route handler?
            // route.ts catches error and returns ApiResponseHelper.handleError

            // Check response status if possible, or mocked return
            // Currently route.ts returns NextResponse.
            // We need to parse it. 
            // Since we running inside jest environment node, NextResponse might behave differently or needs polyfill.
            // Assuming standard Next.js behavior or helper response.

            const json = await res.json();
            expect(res.status).toBe(403); // Our global handler sets 403 for Forbidden
        });

        it('should allow user with ADMIN role', async () => {
            const session = createMockSession({
                roles: ['ADMIN'],
                userId: 'user-admin',
                username: 'admin',
                // @ts-ignore
                empresa_id: tenantA.id
            });
            // Inject empresa_id manually as createMockSession might not have it in types yet
            session.user.empresa_id = tenantA.id;

            (requireAuth as jest.Mock).mockResolvedValue(session);

            const { req } = createMocks({ method: 'GET' });
            // @ts-ignore
            const res = await GET(req);

            expect(res.status).toBe(200);
        });
    });

    describe('Multi-tenant Isolation', () => {
        it('should isolate webhooks between tenants', async () => {
            // 1. Create Webhook for Tenant A
            const sessionA = createMockSession({ roles: ['ADMIN'], userId: userA.id, username: 'admin-a' });
            sessionA.user.empresa_id = tenantA.id;
            (requireAuth as jest.Mock).mockResolvedValue(sessionA);

            const { req: reqPostA } = createMocks({
                method: 'POST',
                json: async () => ({
                    nombre: 'Webhook A',
                    url: 'https://a.com',
                    eventos: ['ALL_EVENTS'],
                    secret: 'secret-a-123'
                })
            });
            // @ts-ignore
            const resPostA = await POST(reqPostA);
            const jsonA = await resPostA.json();

            // If creation fails, we fail fast to know why
            if (resPostA.status !== 201) {
                console.error('POST A Failed:', jsonA);
            }
            expect(resPostA.status).toBe(201);

            // 2. Create Webhook for Tenant B
            const sessionB = createMockSession({ roles: ['ADMIN'], userId: userB.id, username: 'admin-b' });
            sessionB.user.empresa_id = tenantB.id;
            (requireAuth as jest.Mock).mockResolvedValue(sessionB);

            const { req: reqPostB } = createMocks({
                method: 'POST',
                json: async () => ({
                    nombre: 'Webhook B',
                    url: 'https://b.com',
                    eventos: ['ALL_EVENTS'],
                    secret: 'secret-b-123'
                })
            });
            // @ts-ignore
            const resPostB = await POST(reqPostB);
            expect(resPostB.status).toBe(201);

            // 3. Query as Tenant A - Should ONLY see Webhook A
            (requireAuth as jest.Mock).mockResolvedValue(sessionA);
            const { req: reqGetA } = createMocks({ method: 'GET' });
            // @ts-ignore
            const resA = await GET(reqGetA);
            const dataA = await resA.json();

            const webhooksA = dataA.data || dataA; // Handle generic response wrapper
            expect(webhooksA).toHaveLength(1);
            expect(webhooksA[0].nombre).toBe('Webhook A');

            // 4. Query as Tenant B - Should ONLY see Webhook B
            (requireAuth as jest.Mock).mockResolvedValue(sessionB);
            const { req: reqGetB } = createMocks({ method: 'GET' });
            // @ts-ignore
            const resB = await GET(reqGetB);
            const dataB = await resB.json();

            const webhooksB = dataB.data || dataB;
            expect(webhooksB).toHaveLength(1);
            expect(webhooksB[0].nombre).toBe('Webhook B');
        });
    });
});
