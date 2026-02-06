import { NextRequest, NextResponse } from 'next/server';
import { Session } from 'next-auth';
import { ZodSchema } from 'zod';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
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
    handler?: ApiHandlerFunction; // Support object-style call
}

/**
 * Wraps an API Route handler with standardized error handling, authentication, 
 * permission checking, and validation.
 * 
 * Supports two call patterns:
 * 1. apiHandler(fn, { permission... }) - Traditional
 * 2. apiHandler({ handler: fn, permission... }) - Object-style
 */
export function apiHandler(
    handlerOrOptions: ApiHandlerFunction | ApiHandlerOptions,
    options: ApiHandlerOptions = {}
) {
    // Normalize arguments - support both call patterns
    let handler: ApiHandlerFunction;
    let opts: ApiHandlerOptions;

    if (typeof handlerOrOptions === 'function') {
        // Pattern 1: apiHandler(fn, options)
        handler = handlerOrOptions;
        opts = options;
    } else {
        // Pattern 2: apiHandler({ handler, ...options })
        if (!handlerOrOptions.handler) {
            throw new Error('apiHandler: handler function is required');
        }
        handler = handlerOrOptions.handler;
        opts = handlerOrOptions;
    }

    return async (req: NextRequest, context: ApiContext) => {
        try {
            // 1. Authentication
            const session = await requireAuth();

            // 2. Authorization (Permissions)
            if (opts.permission) {
                await requirePermission(session, opts.permission as any);
            }

            // 3. Authorization (Roles - Optional specific check)
            if (opts.roles && opts.roles.length > 0) {
                if (!opts.roles.some(role => session.user.roles.includes(role))) {
                    return ApiResponseHelper.forbidden('Rol no autorizado');
                }
            }

            // 4. Body Validation (if schema provided)
            let body = undefined;
            if (opts.schema) {
                try {
                    const json = await req.json();
                    const validation = opts.schema.safeParse(json);

                    if (!validation.success) {
                        return ApiResponseHelper.validationError(formatZodErrors(validation.error));
                    }
                    body = validation.data;
                } catch (e) {
                    return ApiResponseHelper.error('Invalid JSON body', 400);
                }
            }

            // 5. Execute Handler
            const result = await handler(req, session, context, body);

            // 6. Normalize Response 
            if (result instanceof NextResponse) {
                return result;
            }

            return ApiResponseHelper.success(result);

        } catch (error) {
            return ApiResponseHelper.handleError(error);
        }
    };
}
