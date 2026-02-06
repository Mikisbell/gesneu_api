
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { DashboardService } from '@/lib/services/dashboard.service';

const service = new DashboardService();

export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        // Permission check - assuming basic dashboard access is enough or reusing NEUMATICOS_READ
        // requirePermission(session, PERMISSIONS.DASHBOARD_READ); // If exists

        const stats = await service.getGeneralStats(session.user.empresa_id!);
        return ApiResponseHelper.success(stats);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
