import { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { createAuditLog, AuditAction } from '@/lib/audit';

export async function auditRequest(
    req: NextRequest,
    action: AuditAction,
    resource: string,
    details?: Record<string, any>
) {
    try {
        const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });
        if (token?.sub) {
            await createAuditLog({
                userId: token.sub,
                action,
                resource,
                details,
                ipAddress: req.headers.get('x-forwarded-for') || undefined,
            });
        }
    } catch (error) {
        console.error('Audit middleware error:', error);
    }
}
