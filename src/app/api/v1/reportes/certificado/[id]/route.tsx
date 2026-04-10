import { NextRequest, NextResponse } from 'next/server';
import React from 'react';
import ReactPDF from '@react-pdf/renderer';
import { CertificadoOperatividadDocument } from '@/components/reports/CertificadoDocument';
import { requireAuth } from '@/lib/auth/authorization';
import { emitirCertificadoOperatividad } from '@/lib/services/certificado.service';

/**
 * GET /api/v1/reportes/certificado/[id]
 *
 * Emite un certificado de operatividad para un vehículo y retorna el PDF.
 *
 * Características:
 * - Folio secuencial único por empresa (persistido en DB)
 * - Evaluación real de operatividad (APTO / CONDICIONAL / NO_APTO)
 * - Snapshot inmutable del estado del vehículo al momento de emisión
 * - Filtro por empresa_id (protección IDOR)
 * - Cada descarga emite un certificado nuevo con folio trazable
 */
export async function GET(
    _request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();

        if (!session.user.empresa_id) {
            return new NextResponse('Usuario sin empresa asignada', {
                status: 403,
            });
        }

        const { id } = await params;

        // Emisión del certificado (lógica de negocio + persistencia + folio atómico)
        const certificado = await emitirCertificadoOperatividad({
            vehiculoId: id,
            emitidoPor: session.user.id,
            empresaId: session.user.empresa_id,
        });

        // Preparar datos para el componente PDF
        const neumaticosData = certificado.evaluacion.neumaticos.map((n) => ({
            posicion: n.posicion,
            marca: n.marca,
            modelo: n.modelo,
            presion_psi: n.presion_psi,
            profundidad_mm: n.profundidad_mm,
            estado: n.estado as 'APTO' | 'CONDICIONAL' | 'NO_APTO',
        }));

        const fechaEmisionFormateada = certificado.fecha_emision.toLocaleString(
            'es-PE',
            {
                dateStyle: 'short',
                timeStyle: 'short',
            }
        );

        const fechaInspeccionFormateada = certificado.inspeccion.fecha
            ? certificado.inspeccion.fecha.toLocaleDateString('es-PE')
            : null;

        // Generar stream PDF
        const stream = await ReactPDF.renderToStream(
            <CertificadoOperatividadDocument
                folio={certificado.folio_numero}
                fechaEmision={fechaEmisionFormateada}
                vehiculo={certificado.vehiculo}
                inspeccion={{
                    fecha: fechaInspeccionFormateada,
                    inspector: certificado.inspeccion.inspector,
                }}
                resultado={{
                    estado: certificado.estado_operatividad as
                        | 'APTO'
                        | 'CONDICIONAL'
                        | 'NO_APTO',
                    razones: certificado.evaluacion.razones,
                }}
                neumaticos={neumaticosData}
            />
        );

        const filename = `certificado-${certificado.vehiculo.placa}-${certificado.folio_numero
            .toString()
            .padStart(6, '0')}.pdf`;

        return new NextResponse(stream as unknown as ReadableStream, {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `attachment; filename="${filename}"`,
            },
        });
    } catch (error) {
        const message =
            error instanceof Error ? error.message : 'Error desconocido';
        console.error('Error generating certificate PDF:', error);

        if (message.includes('no encontrado') || message.includes('no pertenece')) {
            return new NextResponse(message, { status: 404 });
        }

        return new NextResponse(
            JSON.stringify({ error: message }),
            {
                status: 500,
                headers: { 'Content-Type': 'application/json' },
            }
        );
    }
}
