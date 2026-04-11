import { NextRequest, NextResponse } from 'next/server';

/**
 * @deprecated Endpoint bloqueado por deuda técnica de schema.
 *
 * GET /api/v1/reportes/historial-posicion
 *
 * Este endpoint pretende retornar el historial de instalaciones en una posición
 * específica de un vehículo. Está bloqueado porque el método del service
 * (ReportesService.getHistorialPosicion) fue escrito asumiendo campos del modelo
 * EventoNeumatico que no existen en el schema real:
 *
 *   - empresa_id       (no existe en EventoNeumatico)
 *   - posicion_origen  (no existe — solo hay posicion_montaje_id)
 *   - posicion_destino (no existe — idem)
 *   - km_vehiculo      (el campo real es contador_vehiculo)
 *
 * También usa 'MONTAJE' como valor de TipoEventoNeumaticoEnum cuando el
 * canónico es 'INSTALACION'.
 *
 * Verificado que NINGÚN consumidor (UI, test, otro service) llama a este
 * endpoint — es dead code productivo. Por eso se bloquea con 501 en lugar
 * de reescribir el método, hasta que un stakeholder confirme que la feature
 * es necesaria y defina la semántica de "historial por posición" para
 * rotaciones.
 *
 * Ver docstring completo en reportes.service.ts → getHistorialPosicion
 * para el plan de reactivación.
 */
export async function GET(_request: NextRequest) {
    return NextResponse.json(
        {
            success: false,
            error: "Feature 'historial por posición' no disponible",
            reason: 'Endpoint bloqueado por deuda técnica de schema (campos posicion_origen/destino/km_vehiculo no existen en EventoNeumatico). Ver reportes.service.ts:getHistorialPosicion para plan de reactivación.',
            code: 'FEATURE_DISABLED',
        },
        {
            status: 501,
            headers: { 'Content-Type': 'application/json' },
        }
    );
}
