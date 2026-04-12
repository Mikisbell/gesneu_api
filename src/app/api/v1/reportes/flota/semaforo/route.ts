import { NextRequest, NextResponse } from 'next/server';

/**
 * @deprecated Endpoint bloqueado — método getSemaphoreMatrix no implementado en ReportesService.
 * Usar /api/v1/reportes/semaforo-medida que SÍ tiene implementación funcional (getSemaforoByMedida).
 */
export async function GET(_request: NextRequest) {
    return NextResponse.json(
        {
            success: false,
            error: "Feature 'semáforo de flota' no disponible",
            reason: 'Método getSemaphoreMatrix no implementado en ReportesService. Usar /api/v1/reportes/semaforo-medida como alternativa.',
            code: 'FEATURE_DISABLED',
        },
        { status: 501 }
    );
}
