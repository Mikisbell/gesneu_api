import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth/auth';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { EventoNeumaticoCreateSchema } from '@/lib/validators/evento-neumatico';
import { ApiResponseHelper } from '@/lib/utils/api-response';

const neumaticoService = new NeumaticoService();

export async function POST(req: Request) {
    try {
        const session = await auth();
        if (!session || !session.user || !session.user.id) {
            return ApiResponseHelper.unauthorized();
        }

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
