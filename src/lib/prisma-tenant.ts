import { prisma } from './prisma';
import { auth } from '@/lib/auth/auth';
import { Prisma } from '@prisma/client';

/**
 * Returns a Prisma Client instance scoped to the current user's tenant (RLS).
 * All operations performed with this client are wrapped in a transaction
 * that sets 'app.current_tenant'.
 */
export async function getAuthenticatedClient() {
    const session = await auth();

    // @ts-ignore - empresa_id injected in config.ts but types might lag
    const tenantId = session?.user?.empresa_id;

    if (!tenantId) {
        throw new Error("RLS Error: User is not authenticated or has no Tenant ID.");
    }

    return prisma.$extends({
        query: {
            $allModels: {
                async $allOperations({ model, operation, args, query }) {
                    // Wrap every operation in a transaction to enforce RLS context
                    return prisma.$transaction(async (tx) => {
                        // 1. Set the RLS context variable
                        await tx.$executeRawUnsafe(
                            `SELECT set_config('app.current_tenant', '${tenantId}', true)`
                        );

                        // 2. Re-execute the operation within the transaction context
                        // We cast tx to any because accessing dynamic model/op is not strictly typed
                        if (!model) return (query as any)(args); // Raw queries or non-model ops

                        return (tx as any)[model][operation](args);
                    });
                },
            },
        },
    });
}
