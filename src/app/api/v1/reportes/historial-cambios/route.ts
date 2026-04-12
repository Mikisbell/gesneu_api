import { NextRequest, NextResponse } from 'next/server';

/**
 * @deprecated Endpoint bloqueado — método getChangeHistory no implementado en ReportesService.
 */
export async function GET(_request: NextRequest) {
    return NextResponse.json(
        {
            success: false,
            error: "Feature 'historial de cambios' no disponible",
            reason: 'Método getChangeHistory no implementado en ReportesService.',
            code: 'FEATURE_DISABLED',
        },
        { status: 501 }
    );
}
