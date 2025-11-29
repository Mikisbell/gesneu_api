export type AuditAction = 'CREATE' | 'UPDATE' | 'DELETE' | 'LOGIN' | 'LOGOUT' | 'VIEW' | 'ERROR';

interface CreateAuditLogParams {
    userId: string;
    action: AuditAction;
    resource: string;
    details?: Record<string, any>;
    ipAddress?: string;
}

/**
 * Audit log creation - Currently disabled as auditLog model doesn't exist in simplified schema
 * TODO: Re-implement when audit logging is added back to schema
 */
export async function createAuditLog({
    userId,
    action,
    resource,
    details,
    ipAddress,
}: CreateAuditLogParams) {
    // No-op - audit logging disabled in simplified schema
    // Logs to console instead for development
    if (process.env.NODE_ENV === 'development') {
        console.log('Audit Log:', { userId, action, resource, details, ipAddress });
    }
}
