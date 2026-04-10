import { auth } from '@/lib/auth/auth';
import { TenantService } from '@/lib/services/tenant.service';
import { requireRole, requireAuth } from '@/lib/auth/authorization';
import bcrypt from 'bcryptjs';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { MULTI_TENANT_ENABLED, featureDisabledResponse } from '@/lib/features';

export async function POST(req: Request) {
    if (!MULTI_TENANT_ENABLED) {
        return featureDisabledResponse(
            'Gestión multi-tenant',
            'El sistema opera en modo single-tenant. Gestión de empresas no disponible hasta activar multi-tenant.'
        );
    }

    try {
        // 1. Auth & Role Check
        const session = await requireAuth();
        requireRole(session, ['SUPERADMIN', 'ADMIN']);

        const body = await req.json();

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(body.adminPassword || 'temporal123', salt);

        // 2. Call Service
        const result = await TenantService.createTenant({
            nombre: body.nombre,
            ruc: body.ruc,
            direccion: body.direccion,
            adminEmail: body.adminEmail,
            adminName: body.adminName,
            adminPasswordHash: hashedPassword
        });

        return ApiResponseHelper.created(result);

    } catch (error: any) {
        console.error('Error creating tenant:', error);
        // Specialized error mapping or let helper handle it
        return ApiResponseHelper.handleError(error);
    }
}

export async function GET(req: Request) {
    if (!MULTI_TENANT_ENABLED) {
        return featureDisabledResponse(
            'Gestión multi-tenant',
            'El sistema opera en modo single-tenant. Gestión de empresas no disponible hasta activar multi-tenant.'
        );
    }

    try {
        const session = await requireAuth();
        requireRole(session, ['SUPERADMIN', 'ADMIN']);

        const tenants = await TenantService.getAllTenants();
        return ApiResponseHelper.success(tenants);
    } catch (error: any) {
        return ApiResponseHelper.handleError(error);
    }
}
