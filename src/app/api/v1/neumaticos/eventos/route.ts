```typescript
import { NextResponse } from 'next/server';
import { requireAuth } from '@/lib/auth/authorization';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { EventoNeumaticoCreateSchema } from '@/lib/validators/evento-neumatico';
import { ApiResponseHelper } from '@/lib/utils/api-response';

const neumaticoService = new NeumaticoService();

export async function POST(req: Request) {
    try {
        const session = await requireAuth();

        const body = await req.json();

        // 1. Validación de Entrada con Zod
        const validation = EventoNeumaticoCreateSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error as any);
        }

        // 2. Ejecución Lógica Transaccional
        const resultado = await neumaticoService.registrarEvento(
            validation.data,
            session.user.id
        );

        return ApiResponseHelper.success(resultado, 'Evento registrado correctamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
