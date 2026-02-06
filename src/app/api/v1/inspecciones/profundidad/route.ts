import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/auth/authorization';
import { InspeccionService } from '@/lib/services/inspeccion.service';
import { registerObservers } from '@/lib/events/registry';

// Ensure observers are registered
registerObservers();

const service = new InspeccionService();

/**
 * POST /api/v1/inspecciones/profundidad
 * Body: { neumatico_id, profundidad_int, profundidad_cen, profundidad_ext, kilometraje?, observaciones? }
 */
export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();

        const body = await request.json();
        const {
            neumatico_id,
            profundidad_int,
            profundidad_cen,
            profundidad_ext,
            kilometraje,
            observaciones
        } = body;

        if (!neumatico_id || profundidad_int === undefined || profundidad_cen === undefined || profundidad_ext === undefined) {
            return NextResponse.json(
                { error: 'neumatico_id y las 3 mediciones de profundidad son requeridas' },
                { status: 400 }
            );
        }

        const medicion = await service.registrarProfundidad({
            neumaticoId: neumatico_id,
            profundidades: {
                int: Number(profundidad_int),
                cen: Number(profundidad_cen),
                ext: Number(profundidad_ext)
            },
            empresaId: session.user.empresa_id!,
            usuarioId: session.user.id,
            kilometraje: kilometraje ? Number(kilometraje) : undefined,
            observaciones
        });

        return NextResponse.json({
            success: true,
            data: medicion,
            message: 'Medición de profundidad registrada correctamente'
        });

    } catch (error: any) {
        console.error('[API] Error en registro de profundidad:', error);
        return NextResponse.json(
            { error: error.message || 'Error interno' },
            { status: 500 }
        );
    }
}
