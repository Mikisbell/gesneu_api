import { prisma } from '@/lib/prisma';

export type AuditAction = 'CREATE' | 'UPDATE' | 'DELETE' | 'LOGIN' | 'LOGOUT' | 'VIEW' | 'ERROR';

interface CreateAuditLogParams {
    userId: string;
    action: AuditAction;
    resource: string;
    details?: Record<string, any>;
    ipAddress?: string;
}

export async function createAuditLog({
    userId,
    action,
    resource,
    details,
    ipAddress,
}: CreateAuditLogParams) {
    try {
        await prisma.auditLog.create({
            data: {
                user_id: userId,
                action,
                resource,
                details: details || {},
                ip_address: ipAddress,
            },
        });
    } catch (error) {
        console.error('Error creating audit log:', error);
        // Don't throw error to avoid blocking the main operation
    }
}
