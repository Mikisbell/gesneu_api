import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { InspeccionNeumaticoSchema } from '@/lib/validators/inspeccion';

export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación y autorización
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION);

        // 2. Validar entrada
        const body = await request.json();
        const validatedData = InspeccionNeumaticoSchema.parse(body);

        // 3. Validar existencia del neumático
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: validatedData.neumatico_id },
            include: { ubicacion_vehiculo: true }
        });

        if (!neumatico) {
            return ApiResponseHelper.notFound();
        }

        // 4. Registrar inspección como evento
        const evento = await prisma.eventoNeumatico.create({
            data: {
                tipo_evento: 'INSPECCION',
                neumatico_id: neumatico.id,
                fecha_evento: new Date(),
                contador_vehiculo: validatedData.contador_vehiculo,
                presion_psi: validatedData.presion_psi,
                profundidad_remanente: validatedData.profundidad_mm,
                notas: validatedData.observaciones,
                creado_por: session.user.id,
                vehiculo_id: neumatico.ubicacion_vehiculo_id
            }
        });

        return ApiResponseHelper.success({
            evento
        }, 'Inspección registrada exitosamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
