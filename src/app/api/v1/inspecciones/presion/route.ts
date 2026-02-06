import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/auth/authorization';
import { InspeccionService } from '@/lib/services/inspeccion.service';
import { registerObservers } from '@/lib/events/registry';

// Ensure observers are registered
registerObservers();

const service = new InspeccionService();

/**
 * POST /api/v1/inspecciones/presion
 * Body: { neumatico_id, presion_psi, temperatura?, fuente? }
 */
export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();

        const body = await request.json();
        const { neumatico_id, presion_psi, temperatura, fuente } = body;

        if (!neumatico_id || presion_psi === undefined) {
            return NextResponse.json(
                { error: 'neumatico_id y presion_psi son requeridos' },
                { status: 400 }
            );
        }

        const lectura = await service.registrarPresion({
            neumaticoId: neumatico_id,
            presionPsi: Number(presion_psi),
            empresaId: session.user.empresa_id!,
            usuarioId: session.user.id,
            fuente: fuente || 'MANUAL',
            temperatura: temperatura ? Number(temperatura) : undefined
        });

        return NextResponse.json({
            success: true,
            data: lectura,
            message: 'Lectura de presión registrada correctamente'
        });

    } catch (error: any) {
        console.error('[API] Error en registro de presión:', error);
        return NextResponse.json(
            { error: error.message || 'Error interno' },
            { status: 500 }
        );
    }
}
