import { NextRequest, NextResponse } from 'next/server';
import { Session } from 'next-auth';
import { ZodSchema } from 'zod';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { Permission } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { formatZodErrors } from '@/lib/utils/zod.utils';

type ApiContext = {
    params: Promise<Record<string, string>> | Record<string, string>;
};

type ApiHandlerFunction = (
    req: NextRequest,
    session: Session,
    context: ApiContext,
    body?: any
) => Promise<NextResponse | any>;

interface ApiHandlerOptions {
    permission?: string;
    schema?: ZodSchema<any>;
    roles?: string[];
}

/**
 * Wraps an API Route handler with standardized error handling, authentication, 
 * permission checking, and validation.
 */
export function apiHandler(
    handler: ApiHandlerFunction,
    options: ApiHandlerOptions = {}
) {
    return async (req: NextRequest, context: ApiContext) => {
        try {
            // 1. Authentication
            const session = await requireAuth();

            // 2. Authorization (Permissions)
            if (options.permission) {
                await requirePermission(session, options.permission as Permission);
            }

            // 3. Authorization (Roles - Optional specific check)
            if (options.roles && options.roles.length > 0) {
                if (!options.roles.includes(session.user.rol)) {
                    return ApiResponseHelper.forbidden('Rol no autorizado');
                }
            }

            // 4. Body Validation (if schema provided)
            let body = undefined;
            if (options.schema) {
                try {
                    const json = await req.json();
                    const validation = options.schema.safeParse(json);

                    if (!validation.success) {
                        const errors = formatZodErrors(validation.error);
                        console.error('❌ Validation Error:', JSON.stringify(errors, null, 2));
                        return ApiResponseHelper.validationError(errors);
                    }
                    body = validation.data;
                } catch (e) {
                    return ApiResponseHelper.error('Invalid JSON body', 400);
                }
            }

            // 5. Execute Handler
            const result = await handler(req, session, context, body);

            // 6. Normalize Response 
            // If handler returns a NextResponse, return it.
            // If it returns data, wrap it in success.
            if (result instanceof NextResponse) {
                return result;
            }

            return ApiResponseHelper.success(result);

        } catch (error) {
            return ApiResponseHelper.handleError(error);
        }
    };
}
